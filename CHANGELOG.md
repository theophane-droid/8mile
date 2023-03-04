# Changelog

## Actual dev branch

- Change of paradigm: this library should now focus on downloading and processing financial data. Any artificial intelligence capabilities must not be included in this library.
- Removed artificial intelligence capabilities.
- Removed rendering capabilities.
- Fixed "Hmile" naming to "hmile".
- Renamed classes in __init__.
- Fixed fill policy call.
- Updated dependency versions.
- Set fillpolicyakima by default : this means that missing values will be filled by default
- setup.py read the dependencies from requirements.txt