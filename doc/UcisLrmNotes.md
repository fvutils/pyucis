
# API vs Schema

## Coverpoint Bin Values

## Coverpoint Cross Components
- The API explicitly associates coverpoints with a cross
- The XML schema doesn't appear to provide an explicit way for this to be doone

- Resolution: Store the cross list in the <crossExpr> element

## Coverpoint Cross Bin Indices
- A coverpoint bin according to the API is a counted object with an arbitrary name.
  No information about the value set is associated with the bin.
- A cover

- Resolution: PyUCIS emits bin definitions into the XML output without meaningful
  bin-value information


# Spec vs Schema

## Coverpoint
- Schema is missing 'name' and 'key' attribute

## Cross
- Schema is missing 'name' and 'key' attribute

# Examples vs Spec/Schema

