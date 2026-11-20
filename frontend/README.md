# PlateCheck Python frontend prototype

From the repository root:

```bash
python3 -m pip install -r frontend/requirements.txt
python3 -m streamlit run frontend/app.py
```

The page previews a PNG/JPEG meal photo and displays clearly labeled sample nutrition data. Item amounts can be changed, added, or removed; totals update in the browser. The photo is not analyzed by a model.

## Code layout

- `app.py`: Streamlit controls and display only.
- `platecheck_ui/models.py`: shared food-item and nutrition data structures.
- `platecheck_ui/nutrition.py`: deterministic per-item and meal totals, independent of Streamlit.
- `platecheck_ui/demo.py`: illustrative values used until real results are available.

The nutrition calculations have no UI dependency, so they can be reused when C1 segmentation and C2 mass prediction feed C3. Run the small calculation checks with `python3 -m unittest discover -s frontend/tests`.

## Next integration step

Agree with the inference-server owner on units and response fields. The current server response has `name`, `quantity`, `protein`, `carbs`, and `fat`, but does not define whether these are per-item totals or per-gram values and does not include calories. Once that contract is fixed, add a separate adapter that converts the server response into `FoodItem` objects. Keep the Streamlit view and nutrition functions unchanged where possible.

The current server defines `POST /calculate`, but its implementation raises `NotImplementedError`. The sample per-gram values in `platecheck_ui/demo.py` are for UI demonstration only and must not be used as a validated nutrition lookup.
