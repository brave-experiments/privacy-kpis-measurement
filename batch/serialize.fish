#!/usr/bin/env fish
# Use: ./serialize.fish <path to serialize.py> <path to json files> <path to pickle to>

set SCRIPT_PATH $argv[1];
set GRAPH_DIR $argv[2];
set OUTPUT_DIR $argv[3];

if not test -f "$SCRIPT_PATH";
  echo "First arg should be path to the ./serialize.py script."; 
  exit 1;
end;

if not test -d "$GRAPH_DIR";
  echo "Second arg should be path of json data."; 
  exit 1;
end;

if not test -d "$OUTPUT_DIR";
  echo "Third arg should be directory to write results to.";
  exit 1;
end;

for BROWSER in chrome-ubo firefox chrome chrome-brave safari;
  for DATASET in twitter alexa;
    for CASE in 1 2;
      set DESC "$BROWSER-$DATASET-$CASE";
      set OUTPUT_PATH $OUTPUT_DIR/$DESC.pickle;
      set INPUTS (ls $GRAPH_DIR/$DESC-*);
      echo $DESC;
      if test -f $OUTPUT_PATH;
        continue;
      end;
      ./serialize.py --debug -r /tmp/redirects.pickle --input $INPUTS --multi --output $OUTPUT_PATH;
    end;
  end;
end;
