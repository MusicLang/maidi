import numpy as np
import time
import os
import requests
import tempfile
import warnings
from maidi.integrations.base import MidiApiIntegration
from maidi.integrations.api.musiclang import models
from maidi import MidiScore
from maidi import constants


# Enum of models

def get_musiclang_tag_list():
    from maidi.analysis.tags_providers import DensityTagsProvider, MinMaxPolyphonyTagsProvider,MinMaxRegisterTagsProvider, SpecialNotesTagsProvider
    tag_providers= [DensityTagsProvider, MinMaxPolyphonyTagsProvider, MinMaxRegisterTagsProvider, SpecialNotesTagsProvider]
    all_tags = []
    for tag_provider in tag_providers:
        provider = tag_provider()
        all_tags += provider.get_tags_list()

    return set(all_tags)


AVAILABLE_TAGS = get_musiclang_tag_list()


class MusicLangAPI(MidiApiIntegration):
    """
    Class to interact with the MusicLang API from a maidi.MidiScore

    **Usage:**


    >>> import os
    >>> import numpy as np
    >>> API_URL = os.getenv("API_URL")
    >>> MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")
    >>> from maidi.integrations.api import MusicLangAPI
    >>> from maidi import MidiScore,instrument
    >>> api = MusicLangAPI(API_URL, MUSICLANG_API_KEY)
    >>> score = MidiScore.from_empty(instruments=[instrument.PIANO, instrument.ELECTRIC_BASS_FINGER], nb_bars=4, ts=(4, 4), tempo=120)
    >>> mask = np.ones((2, 4))
    >>> predicted_score = api.predict(score, mask, model="control_masking_large", timeout=120, temperature=0.95)
    >>> predicted_score.write("predicted_score.mid")


    """
    PREDICT_ASYNC_ENDPOINT = "predict_long"
    PREDICT_SYNC_ENDPOINT = "predict"
    POLLING_ENDPOINT = "polling_predict"
    MAX_CONTEXT = 16 # Maximum context size of 16 bars for all masking models

    def __init__(self, api_key=None, api_url='https://api.musiclang.io', verbose=False):
        """
        Initialize the MusicLangAPI class

        Parameters
        ----------
        api_url : str
            URL of the API
        api_key : str
            Your secret API key to use
        verbose : bool
            If True, print debug information (Default value = False)

        """
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key

        if self.api_key is None:
            # Get env
            self.api_key = os.getenv(constants.MUSICLANG_API_KEY_VARIABLE, None)
        if self.api_key is None:  # If not in env and not passed as a variable, raise an error
            raise ValueError('API key missing')

        self.verbose = verbose

    def _predict_with_api(
            self,
            score,
            mask,
            model="control_masking_large",
            temperature=0.95,
            async_mode=False,
            polling_interval=1,
            chords=None,
            tags=None,
            **prediction_kwargs,
    ):
        """

        Parameters
        ----------
        mask : np.array, shape (n_tracks, n_bars)
            The mask to use for the prediction
        model : str, optional, (Default value = "control_masking_large")
            The choice of model to use
        temperature : float, (Default value = 0.95)
            The temperature for the model, don't go higher than 1.0
        async_mode : bool, optional, (Default value = False)
            If True, return the task id, otherwise wait for the request to finish with polling
        polling_interval : int, optional, (Default value = 1)
            Interval in seconds to poll the API
        **prediction_kwargs :
            Additional arguments for the model (for example chord and control tags)

        Returns
        -------

        """

        if model in models.ONLY_SYNC_MODELS:
            if async_mode:
                raise ValueError(f"Model {model} does not support async mode, use async_mode=False")
            return self._predict_with_api_optimized(
                score,
                mask,
                model=model,
                temperature=temperature,
                async_mode=async_mode,
                polling_interval=polling_interval,
                chords=chords,
                tags=tags,
                **prediction_kwargs,
            )

        # Otherwise we are not using an optimized model
        mask = np.asarray(mask)
        score.check_mask(mask)
        task_id = self._call_predict_api(
            score.to_base64(), mask, model, temperature, chords, tags, **prediction_kwargs
        )
        if async_mode:
            return task_id
        else:
            score = self.from_task_id(task_id, polling_interval=polling_interval)
        return score


    def _predict_with_api_optimized(self,
                                    score,
                                    mask,
                                    model="control_masking_large",
                                    temperature=0.95,
                                    async_mode=False,
                                    polling_interval=1,
                                    chords=None,
                                    tags=None,
                                    **prediction_kwargs,
                                    ):
        mask = np.asarray(mask)
        score.check_mask(mask)
        result_base64 = self._call_predict_api_sync(
            score.to_base64(), mask, model, temperature, chords, tags, **prediction_kwargs
        )
        score = MidiScore.from_base64(result_base64)
        return score

    def pprint(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)


    def generate_from_scratch(self, instruments, nb_bars, ts, tempo, model=models.MODEL_CONTROL_MASKING_LARGE, chords=None, tags=None, temperature=0.95,
                              **kwargs):
        """Generate a score from scratch with the given parameters

        Parameters
        ----------
        instruments : list[str]
            List of instruments to use
        nb_bars : int
            Number of bars
        ts : tuple
            Time signature
        tempo : int
            Tempo
        model : str
            Model to use (Default value = models.MODEL_CONTROL_MASKING_LARGE)
        chords : list[tuple or None]
            List of chord tuples to guide the generation
        tags : list[list[list]] or None
            Tags to guide the generation
        temperature : float
            Temperature for the model (Default value = 0.95)
        **kwargs :
            Additional arguments for the model to pass to the `predict` method

        **Usage**

        >>> import numpy as np
        >>> from maidi import MidiScore, instrument
        >>> from maidi.integrations.api import MusicLangAPI
        >>> from maidi.integrations.api.musiclang import models
        >>> api = MusicLangAPI(API_URL, MUSICLANG_API_KEY)
        >>> score = api.generate_from_scratch(instruments=[instrument.ELECTRIC_PIANO, instrument.ALTO_SAX], nb_bars=4, ts=(4, 4), tempo=120, model=models.MODEL_CONTROL_MASKING_LARGE, temperature=0.95)
        >>> score.write("generated_score.mid")
        """
        score = MidiScore.from_empty(instruments=instruments, nb_bars=nb_bars, ts=ts, tempo=tempo)
        mask, new_tags, new_chords = score.get_empty_controls(prevent_silence=False)
        if tags is None:
            tags = new_tags
        if chords is None:
            chords = new_chords

        mask[:, :] = 1

        return self.predict(score, mask, model=model, temperature=temperature, chords=chords, tags=tags, **kwargs)

    def check_parameters(self,
                         score,
                         mask,
                         model=models.MODEL_CONTROL_MASKING_LARGE,
                         temperature=0.95,
                         polling_interval=1,
                         tags=None,
                         chords=None,
                         **kwargs
                         ):
        """


        """
        from maidi import TagManager, ChordManager
        mask = np.asarray(mask)
        if model not in models.MODELS:
            raise ValueError(f"Model {model} not existing. Models available : {models.MODELS}")
        if temperature > 1.0:
            raise ValueError("Temperature must be lower than 1.0")
        if polling_interval < 0:
            raise ValueError("Polling interval must be > 0")
        if score.nb_bars > MusicLangAPI.MAX_CONTEXT:
            raise ValueError(f"The prompted score must be less than {MusicLangAPI.MAX_CONTEXT} bars.")

        if tags is not None:
            # Check with tag manager
            tm = TagManager(tags)
            if tm.shape != score.shape:
                raise ValueError(f'Wrong shape for tags, (tags) : {tm.shape} (score) : {score.shape}')

            self._check_tags_exists(tags)

        if score.nb_bars != mask.shape[1]:
            raise ValueError(f'Wrong number of bars in the mask, (score) : {score.nb_bars} (mask): {mask.shape[1]}')

        if score.nb_tracks != mask.shape[0]:
            raise ValueError(f'Wrong number of tracks in the mask, (score) : {score.nb_tracks} (mask): {mask.shape[0]}')

        if chords is not None:
            self._check_chords_exists(chords)

        if chords is not None and (len(chords) != score.nb_bars):
            raise ValueError(f'Wrong number of chords (chords) :{len(chords)} (score) : {score.nb_bars}')

        score.check_mask(mask)

        return mask


    def predict(
            self,
            score,
            mask,
            model=models.MODEL_CONTROL_MASKING_LARGE,
            timeout=120,
            temperature=0.95,
            cut_silenced_bars=False,
            regen_missing_bars=False,
            async_mode=False,
            polling_interval=1,
            tags=None,
            chords=None,
            **prediction_kwargs,
    ):
        """Predict the score with the given mask and prediction parameters

        **Usage**

        >>> import numpy as np
        >>> from maidi import MidiScore
        >>> from maidi.integrations.api import MusicLangAPI
        >>> score = MidiScore.from_empty(instruments=['piano'], nb_bars=4, ts=(4, 4), tempo=120)
        >>> mask = np.ones((1, 4))
        >>> api = MusicLangAPI(API_URL, MUSICLANG_API_KEY)  # Get your API_URL and MUSICLANG_API_KEY here
        >>> predicted_score = api.predict(score, mask, model="control_masking_large", timeout=120, temperature=0.95)
        >>> predicted_score.write("predicted_score.mid")

        Parameters
        ----------
        score : MidiScore
            The score to predict
        mask : np.array of shape (n_tracks, n_bars)
            The mask to use for the prediction
        model :
            str, model to use (for the API) (Default value = "control_masking_large")
        timeout :
            int, timeout for the API (Default value = 120)
        temperature :
            float, temperature for the model (Default value = 0.95)
        cut_silenced_bars :
            bool, if True cut silenced bars at the beginning and end (Default value = False)
        regen_missing_bars :
            bool, if True regenerate missing bars with another call to predict (Default value = False)
        prediction_kwargs :
            dict, additional arguments for the model (specifically `chord` and control `tags`)
        async_mode :
            bool, if True return the task id, otherwise wait for the request to finish with polling (Default value = False)
        polling_interval :
            int, interval in seconds to poll the API, only used if async_mode is False (Default value = 1)

        chords: list[tuple or None ]  or None
            List of tuple (chord_degree, tonality_degree, tonality_mode, roman numeral extension). Check the user guide for more information
        tags: list[list[list]] or None (n_tracks, n_bars, <variable length number of tags>)
            Way to specify soft constraints on the generation for each bar of each track, check the user guide for more information

        **prediction_kwargs :

        Returns
        -------
        score :
            MidiScore or str : predicted score if sync mode

        """

        score_to_predict = score.copy()

        from maidi import TagManager, ChordManager
        if isinstance(tags, TagManager):
            tags = tags.tags
        if isinstance(chords, ChordManager):
            chords = chords.to_chords()
        mask = self.check_parameters(score_to_predict,
                         mask=mask,
                         model=model,
                         temperature=temperature,
                         polling_interval=polling_interval,
                         tags=tags,
                         chords=chords)

        if chords is None:
            chords = [None] * score_to_predict.nb_bars

        result = self._predict_with_api(
            score_to_predict,
            mask,
            model=model,
            timeout=timeout,
            temperature=temperature,
            async_mode=async_mode,
            polling_interval=polling_interval,
            chords=chords,
            tags=tags,
            **prediction_kwargs,
        )
        if async_mode:
            return result  # Return the task id

        score = result
        score = self.sanitize_score(score, score_to_predict, mask)
        # Cut silenced bars if at the end or beginning
        if cut_silenced_bars:
            score = score.cut_silenced_bars_at_beginning_and_end()

        # Regenerate missing bars if necessary
        if regen_missing_bars and score.nb_bars < mask.shape[1]:
            nb_missing_bars = mask.shape[1] - score.nb_bars
            score = score.add_silence_bars(
                mask.shape[1] - score.nb_bars, add_fake_notes=True
            )
            new_mask = score.get_mask()
            new_mask[:, -nb_missing_bars:] = 1
            return self.predict(
                score,
                new_mask,
                model=model,
                timeout=timeout,
                temperature=temperature,
                cut_silenced_bars=cut_silenced_bars,
                regen_missing_bars=regen_missing_bars,
            )
        return score

    def sanitize_score(self, score, score_to_compare, mask):
        """Do checks after predicting a score

        Parameters
        ----------
        score :
            param score_to_compare:
        mask :
            return:
        score_to_compare : MidiScore


        Returns
        -------

        """
        score = score.copy()
        score.check_times()
        if len(score.track_keys) > len(score_to_compare.track_keys):
            # If the model added tracks, we need to remove them
            score = score.get_track_subset(0, len(score_to_compare.track_keys))

        if score.nb_bars > mask.shape[1]:
            score = score.get_score_between(0, mask.shape[1])

        return score

    def _get_subchords_and_subtags(self, chords, tags, index_start, index_end, offset=None):
        chords = chords[index_start:index_end] if chords is not None else None
        if tags is not None:
            tags = [[bar for bar in track[index_start:index_end]] for track in tags]

        if offset is not None:
            if chords is not None:
                chords = ([None] * offset) + chords
            if tags is not None:
                tags = [([[]] * offset) + track for track in tags]
        return chords, tags

    def create_transition(self, score1, score2, nb_bars_transition,
                          model=models.MODEL_CONTROL_MASKING_LARGE,
                          return_all=True,
                          chords=None,
                          tags=None,
                          timeout=120,
                          temperature=0.95,
                          async_mode=False,
                          polling_interval=1,
                          **prediction_kwargs):
        """
        Create a transition between two scores using the MusicLang API.

        Parameters
        ----------
        score1 : MidiScore
            The initial score from which to transition.
        score2 : MidiScore
            The final score to transition to.
        nb_bars_transition : int
            The number of bars to use for the transition.
        model : str, optional
            The model to use for the transition (default is "control_masking_large").
        return_all : bool, optional
            If True, return the full concatenated score with transition, otherwise only the transition part (default is True).
        chords : list[tuple or None], optional
            List of chord tuples to guide the transition.
        tags : list[list[list]], optional
            Tags to guide the transition, provided as a list of lists for each track and bar.
        timeout : int, optional
            Timeout for the API call (default is 120 seconds).
        temperature : float, optional
            Temperature parameter for the model (default is 0.95).
        async_mode : bool, optional
            If True, return the task id, otherwise wait for the request to finish with polling (default is False).
        polling_interval : int, optional
            Interval in seconds to poll the API for completion (default is 1 second).

        Returns
        -------
        MidiScore
            The score with the transition bars added, or only the transition part based on the return_all parameter.

        Raises
        ------
        ValueError
            If the model is not recognized or if the input parameters are invalid.
        """

        self._validate_transition_params(score1, score2, nb_bars_transition)

        nb_bars_score1, nb_bars_score2 = self._calculate_bars_to_take(score1, score2, nb_bars_transition)

        transition_segment = self._create_transition_segment(score1, score2, nb_bars_score1, nb_bars_transition,
                                                             nb_bars_score2)
        mask = self._create_transition_mask(score1.nb_tracks, transition_segment.nb_bars, nb_bars_score1,
                                            nb_bars_transition)
        transition_chords, transition_tags = self._adjust_chords_and_tags(chords, tags)

        transition_result = self.predict(
            transition_segment,
            mask,
            model=model,
            timeout=timeout,
            temperature=temperature,
            async_mode=async_mode,
            polling_interval=polling_interval,
            chords=transition_chords,
            tags=transition_tags,
            **prediction_kwargs
        )

        if async_mode:
            return transition_result  # Return the task id

        return self._concatenate_transition_results(score1, transition_result, score2, nb_bars_score1,
                                                    nb_bars_transition, nb_bars_score2, return_all)

    def _validate_transition_params(self, score1, score2, nb_bars_transition):
        if score1.nb_tracks != score2.nb_tracks:
            raise ValueError('The number of tracks in score1 and score2 must be the same')
        if score1.instruments != score2.instruments:
            warnings.warn(
                'Instruments are different in the two scores, interpreting score2 instruments as score1 instruments')

        if nb_bars_transition > self.MAX_CONTEXT - 4:
            raise ValueError(f"Transition size must be less than {self.MAX_CONTEXT - 4} bars")

    def _calculate_bars_to_take(self, score1, score2, nb_bars_transition):
        nb_bars_score1 = min((self.MAX_CONTEXT - nb_bars_transition) // 2, score1.nb_bars)
        nb_bars_score2 = min(self.MAX_CONTEXT - nb_bars_transition - nb_bars_score1, score2.nb_bars)
        return nb_bars_score1, nb_bars_score2

    def _create_transition_segment(self, score1, score2, nb_bars_score1, nb_bars_transition, nb_bars_score2):
        return score1[:, -nb_bars_score1:].add_silence_bars(nb_bars_transition).concatenate(score2[:, :nb_bars_score2],axis=1)

    def _create_transition_mask(self, nb_tracks, nb_bars, nb_bars_score1, nb_bars_transition):
        mask = np.zeros((nb_tracks, nb_bars))
        mask[:, nb_bars_score1:nb_bars_score1 + nb_bars_transition] = 1
        return mask

    def _adjust_chords_and_tags(self, chords, tags):
        return chords, tags

    def _concatenate_transition_results(self, score1, transition_result, score2, nb_bars_score1, nb_bars_transition,
                                        nb_bars_score2, return_all):
        if return_all:
            final_score = score1[:, :-nb_bars_score1].concatenate(transition_result, axis=1).concatenate(
                score2[:, nb_bars_score2:], axis=1)
        else:
            final_score = transition_result[:, nb_bars_score1:nb_bars_score1 + nb_bars_transition]
        return final_score

    def extend(self, score, nb_bars_added,
               model=models.MODEL_CONTROL_MASKING_LARGE,
               nb_added_bars_step=None,
               chords=None,
               tags=None,
               timeout=120,
               temperature=0.95,
               polling_interval=1,
               **prediction_kwargs):
        """
        Extend the given score by a specified number of bars using the MusicLang API.

        Parameters
        ----------
        score : MidiScore
            The initial score to extend.
        nb_bars_added : int
            The number of bars to add to the score.
        model : str, optional
            The model to use for the extension (default is "control_masking_large").
        nb_added_bars_step : int, optional
            Number of bars to add in each step (if None, the extension will use the maximum context size).
        chords : list[tuple or None], optional
            List of chord tuples to guide the extension.
        tags : list[list[list]], optional
            Tags to guide the extension, provided as a list of lists for each track and bar.
        timeout : int, optional
            Timeout for the API call (default is 120 seconds).
        temperature : float, optional
            Temperature parameter for the model (default is 0.95).
        polling_interval : int, optional
            Interval in seconds to poll the API for completion (default is 1 second).
        **prediction_kwargs : dict
            Additional arguments for the model

        Returns
        -------
        MidiScore
            The extended score with the specified number of additional bars.

        Raises
        ------
        ValueError
            If the model is not recognized or if the input parameters are invalid.
        """
        from maidi import TagManager, ChordManager
        if isinstance(chords, ChordManager):
            chords = chords.to_chords()
        if isinstance(chords, str):
            chords = ChordManager.from_roman_string(chords).to_chords()
        if isinstance(tags, TagManager):
            tags = tags.tags
        cm = ChordManager(chords) if chords is not None else None
        tm = TagManager(tags) if tags is not None else None

        if cm is not None:
            # Check size
            if len(cm) != nb_bars_added:
                raise ValueError(f'Wrong number of chords (chords) :{len(cm)} (score) : {score.nb_bars}')
        if tm is not None:
            if tm.shape[0] != score.shape[0]:
                raise ValueError(f'Wrong number of tracks in tags (tags) :{tm.shape[0]} (score) : {score.nb_tracks}')
            if tm.shape[1] != nb_bars_added:
                raise ValueError(f'Wrong number of bars in tags (tags) :{tm.shape[1]} (score) : {nb_bars_added}')

        new_score = score.copy()
        nb_bars_current = new_score.nb_bars
        offset_bar = 0

        if nb_added_bars_step is None:
            nb_added_bars_step = self.MAX_CONTEXT//2

        while new_score.nb_bars < (nb_bars_current + nb_bars_added):
            remaining_bars = (nb_bars_current + nb_bars_added) - new_score.nb_bars
            nb_added_bars_in_this_step = self._determine_bars_step(nb_added_bars_step, remaining_bars)
            new_score = new_score.add_silence_bars(nb_added_bars_in_this_step, add_fake_notes=True)
            predicted_score = new_score[:, -self.MAX_CONTEXT:]
            base_score = new_score[:, :-predicted_score.nb_bars]

            mask = self._create_mask(predicted_score, nb_added_bars_in_this_step)
            subchords, subtags = self._get_subchords_and_subtags(chords, tags, offset_bar,
                                                                 offset_bar+nb_added_bars_in_this_step,
                                                                 mask.shape[1] - nb_added_bars_in_this_step)

            offset_bar += nb_added_bars_in_this_step
            result_predicted_score = self.predict(predicted_score, mask, model, tags=subtags, chords=subchords,temperature=temperature, polling_interval=polling_interval, timeout=timeout, **prediction_kwargs)
            if result_predicted_score.nb_bars < mask.shape[1]:
                print('stopping generation')
                return new_score
                #raise ValueError(f'Error in the API, the number of bars returned is less than the number of bars expected in the mask. Expected : {mask.shape[1]}, got : {result_predicted_score.nb_bars}')
            new_score = base_score.concatenate(result_predicted_score, axis=1)

        return new_score


    def create_variation(self, midi_path, temperature=0.6, **predict_kwargs):
        """
        Create a variation of the given MIDI file using the MusicLang API.
        The midi file can be of any length.
        It will generate a score constrained by the tags and the chord progression of the original file
        It can be useful if you want to generate new ideas from an existing piece of music.

        Parameters
        ------------

        midi_path: str
            The path of the midi file you want to create a variation on
        temperature: float
            The temperature for the model (default is 0.6)
        **predict_kwargs:
            Additional arguments to be passed to the predict method
        """
        from maidi import ScoreTagger
        init_nb_bars = 16
        full_score = MidiScore.from_midi(midi_path)
        total_bars = full_score.nb_bars

        chords = full_score.get_chord_manager(use_last_chord_for_silence=False)
        tags = ScoreTagger.get_base_tagger().tag_score(full_score)

        chords_init = chords[:init_nb_bars]
        tags_init = tags[:, :init_nb_bars]
        remaining_chords = chords[init_nb_bars:]
        remaining_tags = tags[:, init_nb_bars:]

        score = full_score.get_score_between(0, init_nb_bars)
        mask = score.get_mask()
        mask[:, :] = 1

        predicted_score = self.predict(score, mask, model='control_masking_large',
                                      temperature=temperature, tags=tags_init,
                                      chords=chords_init,
                                       **predict_kwargs
                                      )
        if total_bars - init_nb_bars > 0:
            predicted_score = self.extend(predicted_score, (total_bars - init_nb_bars),
                                         chords=remaining_chords,
                                         tags=remaining_tags, temperature=temperature, **predict_kwargs)
        return predicted_score

    def _determine_bars_step(self, nb_added_bars_step, remaining_bars):
        if nb_added_bars_step is not None:
            return min(remaining_bars, nb_added_bars_step)
        else:
            return min(self.MAX_CONTEXT, remaining_bars)

    def _create_mask(self, predicted_score, nb_added_bars_in_this_step):
        mask = predicted_score.get_mask()
        mask[:, -nb_added_bars_in_this_step:] = 1
        return mask





    def _check_tags_exists(self, tags):
        all_tags = set([el for track in tags for bar in track for el in bar])

        if not AVAILABLE_TAGS.issuperset(all_tags):
            tags_not_existing = all_tags - AVAILABLE_TAGS
            raise ValueError(f'Unexisting tags have been used : {tags_not_existing} This is the list of available tags {AVAILABLE_TAGS}')

    def _check_chords_exists(self, chords):
        from maidi.chords_symbols import is_valid_extension, ALL_EXTENSIONS
        def check_chord_exist(chord, index_chord):
            deg, tone, mode, extension = chord
            if not isinstance(deg, int) or deg < 0 or deg > 6:
                raise ValueError(f'Chord degree is wrong : {deg}. It should be an integer between 0 and 6 included')
            if not isinstance(tone, int) or tone < 0 or tone > 11:
                raise ValueError(f'Tonality degree is wrong : {tone}. It should be an integer between 0 and 11 included')
            if not (mode in ['m', 'M']):
                raise ValueError(f'Scale mode is wrong, it should be either "m" (minor mode) or "M" (major mode)')
            if not is_valid_extension(extension):
                raise ValueError(f'Wrong extension : {extension}, must be in {ALL_EXTENSIONS} with optionally added "(sus2)" or "(sus4)"')

        if chords is None:
            return
        for idx, chord in enumerate(chords):
            if chord is not None:
                check_chord_exist(chord, index_chord=idx)



    def _call_polling_api(self, task_id):
        """

        Parameters
        ----------
        url :

        key :

        task_id :


        Returns
        -------

        """
        url = os.path.join(self.api_url, self.POLLING_ENDPOINT, task_id)
        headers = {"x-api-key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def from_task_id(self, task_id, polling_interval=1, timeout=3000):
        """Create a score from a task id by calling the API polling endpoint each polling_interval seconds
        until completion or failure.

        **Usage**

        >>> import numpy as np
        >>> import time
        >>> from maidi import MidiScore
        >>> from maidi.integrations.api import MusicLangAPI
        >>> score = MidiScore.from_empty(instruments=['piano'], nb_bars=4, ts=(4, 4), tempo=120)
        >>> mask = np.ones((1, 4))
        >>> api = MusicLangAPI(API_URL, MUSICLANG_API_KEY)
        >>> task_id = api.predict(score, mask, async_mode=True)
        >>> score = api.from_task_id(task_id, polling_interval=3) # Wait for the task to complete by polling the API every 3 seconds

        Parameters
        ----------
        task_id :
            str, task identifier you got from the predict call
        polling_interval :
            int, interval in seconds to poll the API (Default value = 1)
        timeout :
            int, timeout in seconds, raise an error if the task is not completed after this time (Default value = 3000)

        Returns
        -------

        """
        total_time = 0
        # Poll the API
        while True:
            if total_time > timeout:
                raise TimeoutError("Timeout reached")
            result = self._call_polling_api(task_id)
            if result["status"] == "COMPLETED":
                break
            elif result["status"] == "FAILED":
                error_message = result['error'] if 'error' in result else 'Unknown error'
                raise ValueError(f"Task failed : {error_message}")

            self.pprint(f"Task {task_id} not completed yet, waiting {polling_interval} seconds")
            time.sleep(polling_interval)
            total_time += polling_interval

        # Download the file
        score = MidiScore.from_base64(result["result"]["midi"])

        return score


    def poll_api(self, task_id):
        """Poll the API with a task id once

        Parameters
        ----------
        task_id :
            str, task identifier you got from the predict call

        Returns
        -------

        result: None or MidiScore

        Raises
        ------
        ValueError
            Task failed

        """
        # Poll the API
        result = self._call_polling_api(task_id)
        if result["status"] == "COMPLETED":
            self.pprint(f"Task {task_id} successfully completed")
            return MidiScore.from_base64(result["result"]["midi"])
        elif result["status"] == "FAILED":
            raise RuntimeError("Task failed")
        self.pprint(f"Task {task_id} not completed yet")

        return None

    def _call_predict_api(
            self, midi_base64, mask, model, temperature, chords, tags, **prediction_kwargs
    ):
        """
        Protected method that actually prepare the payload and call the API

        Parameters
        ----------
        midi_base64 : str
            Base64-encoded midi file

        mask : np.Array
            Array representing which bar of which track to regenerate

        model : str
         Model in model list, check user guide.

        temperature : float
            Temperature of the model, between 0 and 1.0

        **prediction_kwargs : dict
            Other model arguments

        Returns
        -------
            task_id : str

        """
        url = os.path.join(self.api_url, self.PREDICT_ASYNC_ENDPOINT)
        payload = {
            "model": model,
            "temperature": temperature,
            "mask": mask.tolist(),
            "file": midi_base64,
        }
        if tags is not None:
            payload['tags'] = tags
        if chords is not None:
            payload['chords'] = chords

        payload.update(prediction_kwargs)
        headers = {"x-api-key": self.api_key}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["task_id"]

    def _call_predict_api_sync(
            self, midi_base64, mask, model, temperature, chords, tags, **prediction_kwargs
    ):
        """
        Protected method that actually prepare the payload and call the sync endpoint of API (reserved for some models)

        Parameters
        ----------
        midi_base64 : str
            Base64-encoded midi file

        mask : np.Array
            Array representing which bar of which track to regenerate

        model : str
         Model in model list, check user guide.

        temperature : float
            Temperature of the model, between 0 and 1.0

        **prediction_kwargs : dict
            Other model arguments

        Returns
        -------
            task_id : str

        """
        url = os.path.join(self.api_url, self.PREDICT_SYNC_ENDPOINT)
        payload = {
            "model": model,
            "temperature": temperature,
            "mask": mask.tolist(),
            "file": midi_base64,
        }
        if tags is not None:
            payload['tags'] = tags
        if chords is not None:
            payload['chords'] = chords

        payload.update(prediction_kwargs)
        headers = {"x-api-key": self.api_key}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['midi']

    def _create_temp_midi_files(self, score):
        """ """
        prompt_file = tempfile.NamedTemporaryFile(suffix=".txt").name
        output_file = tempfile.NamedTemporaryFile(suffix=".txt").name
        midi_file = tempfile.NamedTemporaryFile(suffix=".mid").name
        output_midi_file = tempfile.NamedTemporaryFile(suffix=".mid").name
        score.write(midi_file)
        return prompt_file, output_file, midi_file, output_midi_file

    def _remove_temp_midi_files(
            self, prompt_file, output_file, midi_file, output_midi_file
    ):
        """

        Parameters
        ----------
        prompt_file :

        output_file :

        midi_file :

        output_midi_file :


        Returns
        -------

        """
        os.remove(prompt_file)
        os.remove(output_file)
        os.remove(midi_file)
        os.remove(output_midi_file)