# List all examples in the examples directory with .py extension and run them.

# Get the directory of this file
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Get the examples directory
EXAMPLES_DIR=$DIR

# List all examples in the examples directory with .py extension (recursive)
EXAMPLES=$(find $EXAMPLES_DIR -name "*.py")

# Run all examples and assert that they run without errors
ERRORS=0
for EXAMPLE in $EXAMPLES ; do
    echo "Running example: $EXAMPLE"
    python $EXAMPLE || ERRORS=$((ERRORS+1))
    echo "Done."
done