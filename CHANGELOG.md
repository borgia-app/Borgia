# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.1.0] - 2019-04-20
### Added
- Managers can now disable self recharging with Lydia without having to mess up their tokens.
- You can now add lydia fee when self recharging. You can set the base and ratio fee parts in the configuration module.

### Fix
- Error when accessing self transfert page.

## [5.0.2] - 2019-02-13
### Security
- Update to Django 2.1.7 for security reasons. See : [security announcement](https://www.djangoproject.com/weblog/2019/feb/11/security-releases/)

## [5.0.1] - 2019-02-02
### Fixed
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

### Fixed
- Accessing vulnerability when user was not in group

### Removed
- Notification system, deprecated.
- Unused group "honnored"
- ghost shop "Association"
