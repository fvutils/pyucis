
## 0.1.2
- Tweaks to merge command and merged-xml output

## 0.1.1
- Tweaks to text reporting

## 0.1.0
- Correct an issue with type-coverage calculation

## 0.0.9
- Adjust dependencies 

## 0.0.8
- Progress on new command format and plug-in architecture
- Labeling this with a new version number just for tracking purposes

## 0.0.7
- Adjust the format of the XML slightly. Now, a single
  cgInstance specifies type coverage, while multiple
  cgInstances specify instance coverage from which 
  type coverage is derived by the reader.

## 0.0.6
- Adjust two aspects of the output XML-file format for
  better compatibility with external tools. 
  - Emit a 'range' element for each coverpoint bin
  - Emit one crossExpr element for each cross component

## 0.0.5
- Add support for ignore and illegal coverpoint bins

## 0.0.3
- Ensure XML file is read back correctly

## 0.0.2
- Ensure coverpoint crosses are properly reported
