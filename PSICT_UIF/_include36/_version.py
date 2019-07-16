## Version number format has the following structure:
## [major release].[minor release].[subversion].[build]
## Latest stable releases are indicated by tagged commits in the repository.

## Two special indicators are used:
##
## 'rc' is appended to a minor release number in preparation for a release.
## It indicates that the release is fundamentally complete, but is undergoing testing.
## Thus, '1.2rc0.n' -> '1.2rc1.n' -> '1.2.0' -> '1.2.0.n' -> '1.2.1'
##
## 'dev' is appended to a minor release or subversion number to indicate versions prior to that release.
## It indicates that these changes are not intended for the previous version of the program.
## Moreover, the changes are specifically new features as opposed to improvements or bugfixes on existing features.
## Thus, '1.2.0' -> '1.3dev.0.n' -> ... -> '1.3rc0.n' -> ... -> '1.3.0'
##
## NB both 'X.Ydev' and 'X.YrcN' *precede* 'X.Y'
## Once a release (including at the subversion level) is published, improvements/bugfixes will be released under re-tagged build numbers. 

## Notes for version numbers prior to 1.3dev and 1.2rc1.2:
## New feature development was indicated using the *previous* version numbers, and the 'dev' tag had not yet been introduced. Disentangling new features from updates/fixes may thus be a non-trivial task.

## Notes for version numbers prior to 1.0.7.0:
## Any version featuring a non-null subsubversion or build number is not guaranteed to be stable.
## Also, version numbers were weird.

version = "1.3dev.0.1"
