import numpy as np
import time
import os
import requests
import tempfile
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
    >>> API_URL = os.getenv("API_URL")
    >>> API_KEY = os.getenv("API_KEY")
    >>> from maidi.integrations.api import MusicLangAPI
    >>> from maidi import MidiScore,instrument
    >>> api = MusicLangAPI(API_URL, API_KEY)
    >>> score = MidiScore.from_empty(instruments=[instrument.PIANO, instrument.ELECTRIC_BASS_FINGER], nb_bars=4, ts=(4, 4), tempo=120)
    >>> mask = np.ones((2, 4))
    >>> predicted_score = api.predict(score, mask, model="control_masking_large", timeout=120, temperature=0.95)
    >>> predicted_score.write("predicted_score.mid")


    """
    PREDICT_ASYNC_ENDPOINT = "predict_long"
    POLLING_ENDPOINT = "polling_predict"
    MAX_CONTEXT = 16 # Maximum context size of 16 bars for all masking models

    def __init__(self, api_url='https://api.musiclang.io', api_key=None, verbose=False):
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
            self.api_key = os.getenv(constants.API_KEY_VARIABLE, None)
        if self.api_key is None:  # If not in env and not passed as a variable, raise an error
            raise ValueError('API key missing')

        self.verbose = verbose


    def pprint(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)


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

        >>> from maidi import MidiScore
        >>> from maidi.integrations.api import MusicLangAPI
        >>> score = MidiScore.from_empty(instruments=['piano'], nb_bars=4, ts=(4, 4), tempo=120)
        >>> mask = np.ones((1, 4))
        >>> api = MusicLangAPI(API_URL, API_KEY)  # Get your API_URL and API_KEY here
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
        type
            MidiScore or str : predicted score if sync mode

        """

        if model not in models.MODELS:
            raise ValueError(f"Model {model} not existing. Models available : {models.MODELS}")
        if temperature > 1.0:
            raise ValueError("Temperature must be lower than 1.0")
        if polling_interval < 0:
            raise ValueError("Polling interval must be > 0")
        if score.nb_bars > MusicLangAPI.MAX_CONTEXT:
            raise ValueError(f"The prompted score must be less than {MusicLangAPI.MAX_CONTEXT} bars.")

        if tags is not None:
            self.check_tags_exists(tags)


        score_to_predict = score.copy()
        mask = np.asarray(mask)
        score_to_predict.check_mask(mask)
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
        score = score.sanitize_score(score_to_predict, mask)
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
            return score.predict(
                new_mask,
                model=model,
                timeout=timeout,
                temperature=temperature,
                cut_silenced_bars=cut_silenced_bars,
                regen_missing_bars=regen_missing_bars,
            )
        return score


    def extend(self, score, nb_bars,
               model=models.MODEL_CONTROL_MASKING_LARGE,
            timeout=120,
            temperature=0.95,
            cut_silenced_bars=False,
            regen_missing_bars=False,
            async_mode=False,
            polling_interval=1,
            **prediction_kwargs):

        raise NotImplementedError('Currently not implemented, but soon, use `predict` instead')


    def check_tags_exists(self, tags):
        all_tags = set([el for track in tags for bar in track for el in bar])

        if not AVAILABLE_TAGS.issuperset(all_tags):
            tags_not_existing = all_tags - AVAILABLE_TAGS
            raise ValueError(f'Unexisting tags have been used : {tags_not_existing} This is the list of available tags {AVAILABLE_TAGS}')



    def create_transition(self, score1, score2, nb_bars_transition,
                          model=models.MODEL_CONTROL_MASKING_LARGE,
                          timeout=120,
                          temperature=0.95,
                          cut_silenced_bars=False,
                          regen_missing_bars=False,
                          async_mode=False,
                          polling_interval=1,
                          **prediction_kwargs,
                          ):
        raise NotImplementedError('Currently not implemented, but soon, use `predict` instead')

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

        >>> from maidi import MidiScore
        >>> from maidi.integrations.api import MusicLangAPI
        >>> import time
        >>> score = MidiScore.from_empty(instruments=['piano'], nb_bars=4, ts=(4, 4), tempo=120)
        >>> mask = np.ones((1, 4))
        >>> api = MusicLangAPI(API_URL, API_KEY)
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
                raise ValueError("Task failed")

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
            raise ValueError("Task failed")
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

    def _predict_with_predictor(
            self,
            score,
            predictor,
            mask,
            model="large",
            timeout=3000,
            temperature=0.95,
            **prediction_kwargs,
    ):
        """

        Not implemented yet.

        Parameters
        ----------
        predictor :

        mask :

        model :
             (Default value = "large")
        timeout :
             (Default value = 3000)
        temperature :
             (Default value = 0.95)
        **prediction_kwargs :


        Returns
        -------

        """
        mask = np.asarray(mask)
        score.check_mask(mask)
        prompt_file, output_file, midi_file, output_midi_file = (
            self._create_temp_midi_files(score)
        )
        score.write(midi_file)
        predictor(
            midi_file,
            output_midi_file,
            prompt_file,
            output_file,
            mask,
            chord_range=(0, mask.shape[1]),
            model=model,
            timeout=timeout,
            temperature=temperature,
            **prediction_kwargs,
        )
        score = MidiScore.from_midi(output_midi_file)
        # Clean up the files
        self._remove_temp_midi_files(
            prompt_file, output_file, midi_file, output_midi_file
        )
        return score

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