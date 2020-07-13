#!/usr/local/bin/fish
# Use ./extract.fish <path to extract.py> <path to graph pickles> <path to pickle to>

set SCRIPT_PATH $argv[1];
set INPUT_DIR $argv[2];
set OUTPUT_DIR $argv[3];

if not test -f "$SCRIPT_PATH";
  echo "First arg should be path to the ./extract.py script."; 
  exit 1;
end;

if not test -d "$INPUT_DIR"
  echo "Second arg should be path of pickled graph data."; 
  exit 1;
end;

if not test -d "$OUTPUT_DIR" 
  echo "Third arg should be directory to write results to."
  exit 1
end;

for BROWSER in chrome-ubo firefox chrome chrome-brave safari;
  for DATASET in twitter alexa;
    set MEASURE_GRAPH_PATH "$INPUT_DIR/$BROWSER-$DATASET-1.pickle";
    set CONTROL_GRAPH_PATH "$INPUT_DIR/$BROWSER-$DATASET-2.pickle";
    set OUTPUT_JSON_PATH "$OUTPUT_DIR/$BROWSER-$DATASET.json";

    if test -f "$OUTPUT_JSON_PATH";
      echo "Skipping, $OUTPUT_JSON_PATH already exists.";
      continue;
    end;

    if not test -f "$MEASURE_GRAPH_PATH";
      echo "Could not find main graph for $BROWSER (expected at $MEASURE_GRAPH_PATH).";
      exit 1;
    end;

    if not test -f "$CONTROL_GRAPH_PATH";
      echo "Could not find control graph for $BROWSER (expected at $CONTROL_GRAPH_PATH).";
      exit 1;
    end;

    echo "Beginning $BROWSER, $DATASET";
    ./$SCRIPT_PATH --input $MEASURE_GRAPH_PATH \
                   --control $CONTROL_GRAPH_PATH \
                   --format json \
                   --output $OUTPUT_JSON_PATH;
  end;
end;
