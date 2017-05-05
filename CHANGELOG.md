### 0.13.1
* restructure __main__ and main along pythonic standards
* reintroduce bin/ansible-review for running from source only

### 0.13.0
* Ensure that the examples live inside the python package
* Use console_script entry point rather than bin/ansible-review
* Fix some minor rule bugs
* Update to version 0.13.0

### 0.12.3
* python3 compatibility
*
### 0.12.2
* ansible-review should respect command line parameters
  for lint and standards directories even if config is not
  present

### 0.12.1
* Don't depend on an RC version of ansible-lint. We rely on
  ansible-lint 3.4.1+ because that allows matchplay to be
  run against non-playbook files (should probably be renamed!)

### 0.12.0
* Ensure inventory scripts are detected as code
* Add `ansible_min_version` declaration
* Call unversioned checks Best Practice rather than Future Standard
* Move `yaml_rolesfile` and `yaml_form_rather_than_key_value` checks
  inside ansible-review
* Update standards and add new ansible-lint rules to back them.
* Allow ansible-review to run from example standards and rules by
  default

### 0.11.1
* Add `importlib` as dependency

### 0.11.0
* Make `repeated_vars` actually work
* Create `Makefile` classification
* Enable filtering of standard rules to run with `-s`

### 0.10.1
* Fix mis-classification of files with .yml suffix

### 0.10.0
* Add check for competing group variables

### 0.9.0
* Tidy up log_level

### 0.8.2
* Allow configuration file location to be specified

### 0.8.0
* Enable required version of ansible-lint to be specified

### 0.7.5
* Use `None` for errors that apply to the whole file

### 0.7.4
* Allow no rules to contain a version

### 0.7.3
* Use release of ansible-lint 3.0.0

### 0.7.2
* Fix another indentation false positive

### 0.7.1
* Yaml indent fix

### 0.7.0
* Split `InventoryVars` into `HostVars` and `GroupVars`
