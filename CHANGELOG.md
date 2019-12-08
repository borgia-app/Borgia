# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [5.1.3] 2019-12-05
### Fix
- [Lydia] Fix fee calculation
- [Lydia] Wording / refactoring of self-creation
- [Users] Repair downloaded excel files / Fix members menu in edit page
- [Users] Fix #115 - Can't validate user edition
- [Shops] Fix product list form
- [Contrib] Bump to django 2.1.11 for security reasons
- [Finances/Users] Fix transaction list page with exceptionnal movements
- [Events] Fix Xlsx upload/download 
- [Events] Add JS for forms
- [Users] Fix lateral menu in user retrieve view

### Changed
- [Events] Event list set initial begin date to 1st day of month


## [5.1.2] 2019-11-21
### Changed
- [Configuration] Add tax for Lydia fee
- [Finances] Adjust Lydia fee calculation (the amount paid equals the desired amount + fee) 
- [Finances] Add transaction column and add changes in labels in the list of transactions
- [Shops] Initially checkup on current month
- [Modules] Block form validation button after sale
- [Modules] Possibility to change category order for each module

### Fix
- [Users] Fix user update (username, avatar and theme)
- [Finances] Fix Lydia callback
- [Configuration] Fix some typo
- [Shops] Fix checkup page latency
- [Shops] Checkup page: Fix the possibility to change dates and filter by products
- [Workboard] Charts only show shops that have user transactions
- [Login] Fix next redirection


## [5.1.1] - 2019-09-17
### Changed
- User list default view now include externals members. New option to only display internals members.
- [Users] Edit form : Add username and avatar fields.
- [Users] Include externals members in users list view

### Fix
- Missing link to stockentry and inventory creation.
- Redirection after user self update.
- Possible missing navigation menu
- Chiefs access to associate group management
- Menu for shops manager
- [Sales] fix 403 error on self sales
- Small fixes in templates


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
