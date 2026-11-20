# PlateCheck frontend prototype

Open `index.html` in a browser. No install or build step is required.

The page previews a local PNG/JPEG meal photo and displays clearly labeled sample nutrition data. Item amounts can be changed, added, or removed; totals update in the browser. The photo is never uploaded and does not affect the sample values.

The current server defines `POST /calculate`, but its implementation raises `NotImplementedError`. Before connecting the UI to real predictions, agree on a response that includes item grams and energy, nutrient units, and how edits trigger recalculation. The sample per-gram values in `app.js` are for UI demonstration only and must not be used as a validated nutrition lookup.
