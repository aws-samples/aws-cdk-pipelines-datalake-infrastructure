# Developer Instructions

## Set up Instructions

Reference the [CDK Instructions](./cdk_instructions.md) for standard CDK project setup.

## Code Quality

We now follow [PEP8](https://www.python.org/dev/peps/pep-0008/) enforced through [flake8](https://flake8.pycqa.org/en/latest/) and [pre-commit](https://pre-commit.com/)

Please install and setup pre-commit before making any commits against this project. Example:

```{bash}
pip install pre-commit
pre-commit install
```

The above will create a git hook which will validate code prior to commits. Configuration for standards can be found in:

* [.flake8](../.flake8)
* [.pre-commit-config.yaml](../.pre-commit-config.yaml)

## Testing

TODO
