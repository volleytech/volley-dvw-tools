# DVW Tools
A tool suite for updating DVW files used with [VolleyStation](https://www.volleystation.com) and [DataVolley](https://www.dataproject.com/Products/EN/en/Volleyball/DataVolley4).

## Available Tools
Below you will find a list of tools for updating DVW files.

### DVW Merger (dvw-merger.py)
Used for merging codes from one DVW file with another. It's often difficult for a single individual to obtain all the information needed for each play within a rally, whether it's a serve, attack, block, or dig. Consider the scenario where two members of a staff are coding a match. In this scenario, one could focus solely on the serve and reception while the other could focus on the attack. This tool then allows you to merge the codes from both members of the staff into one DVW file.

#### Note
As of now, this tool requires that there is at least one DVW file that holds all play codes. For example, this file may include a code such as __*10S.5-__, representing the bare minimum that must be present to record a serve and reception. In this example, the home-team player, whose number is 10, has served the ball; the away-team player, whose number is 5, has passed a 1. The staff member who is responsible for serves and receptions may code __*10ST56A.5-,R4__ for this exact same play. As you can see, this code is much more descriptive. This code can then be matched with the less descriptive code and replaced then merged into a single file.
