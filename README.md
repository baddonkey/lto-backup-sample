# lto-backup-sample

Sample usage of [lto-backup](../lto-backup).

## Setup

Install `lto-backup` from the local checkout in editable mode:

```
pip install -e ..\lto-backup
```

Then run the sample:

```
python app.py
```

## Configuration

The log level is controlled by `logging.json`:

```json
{
  "log_level": "DEBUG"
}
```

Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Defaults to `INFO` if the file is absent.
