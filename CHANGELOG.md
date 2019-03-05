# Changelog
All notable changes to this project will be documented in this file.

## [5.0.2] - 2019-02-13
### Fix
- Update to Django 2.1.7 for security reasons. See : [security announcement](https://www.djangoproject.com/weblog/2019/feb/11/security-releases/)

## [5.0.1] - 2019-02-02
### Fix
- Wrong link in managers workboard

## [5.0.0] - 2019-01-18
### Added
- This changelog file
- When not connected, redirect after login to the page wanted

### Changed
- ENTIRE NAVIGATION SYSTEM (now based on "roles" and not on "groups")
- Versionning now follow the pattern : YYYY.MINOR.PATCH
- Renaming of "specials" group to "externals"
- Renaming of "vice-presidents-internal" group to "vice-presidents"
- Renaming of "gadzarts" group to "members"

### Fix
- Accessing vulnerability when user was not in group

### Removed
- Notification system, deprecated.
- Unused group "honnored"
- ghost shop "Association"
