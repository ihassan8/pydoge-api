# 🧱 ExportableMixin Utility

::: pydoge_api.utils.exporter.ExportMixin
    options:
      show_source: false
      members:
        - export
        - to_dataframe
        - summary
---

## 🔁 Utility Functions

### `handle_dict`

::: pydoge_api.utils.exporter.handle_dict

This ensures that even raw dict responses support `.export()`.

---

### `DictExportable`

::: pydoge_api.utils.exporter.DictExportable

A subclass of `dict` that supports `.export()`, `.to_dataframe()`, `.summary()`.
Used when `output_pydantic=False`.
