"""Streamlit view for the PlateCheck integration project.

The UI currently uses demo data. Replace the data source after the inference
server returns item mass and per-item nutrients with agreed units.
"""

from dataclasses import replace

import streamlit as st

from platecheck_ui.demo import DEMO_FOODS, starting_items
from platecheck_ui.models import FoodItem
from platecheck_ui.nutrition import meal_nutrients


st.set_page_config(page_title="PlateCheck", page_icon="🍽️", layout="wide")
st.title("PlateCheck")
st.caption("Meal photo and editable nutrition · CS 539 frontend prototype")
st.info("Demo mode: nutrition values are illustrative. The photo is not analyzed yet.")

if "items" not in st.session_state:
    st.session_state["items"] = [
        {"id": i, "item": item} for i, item in enumerate(starting_items())
    ]
    st.session_state["next_id"] = len(st.session_state["items"])

photo_col, result_col = st.columns([1, 1.2], gap="large")

with photo_col:
    st.subheader("Meal photo")
    photo = st.file_uploader("Choose a PNG or JPEG photo", type=["png", "jpg", "jpeg"])
    if photo is not None:
        st.image(photo, caption="Photo preview", use_container_width=True)
    else:
        st.caption("Your selected photo will appear here.")

with result_col:
    st.subheader("Nutrition estimate")
    st.caption("Edit amounts or add and remove items to recalculate demo totals.")

    for entry in list(st.session_state["items"]):
        item_id = entry["id"]
        item: FoodItem = entry["item"]
        name_col, amount_col, remove_col = st.columns([2, 1, 1])
        name_col.write(f"**{item.name}**")
        grams = amount_col.number_input(
            f"{item.name} grams", min_value=0, max_value=5000, step=1,
            value=int(item.grams), key=f"grams_{item_id}", label_visibility="collapsed",
        )
        entry["item"] = replace(item, grams=grams)
        if remove_col.button("Remove", key=f"remove_{item_id}"):
            st.session_state["items"] = [
                other for other in st.session_state["items"] if other["id"] != item_id
            ]
            del st.session_state[f"grams_{item_id}"]
            st.rerun()

    with st.form("add_item", clear_on_submit=True):
        new_name = st.selectbox("Add food item", list(DEMO_FOODS))
        new_grams = st.number_input("Amount (g)", min_value=0, max_value=5000, value=100)
        if st.form_submit_button("Add item"):
            st.session_state["items"].append({
                "id": st.session_state["next_id"],
                "item": FoodItem(new_name, new_grams, DEMO_FOODS[new_name]),
            })
            st.session_state["next_id"] += 1
            st.rerun()

    totals = meal_nutrients([entry["item"] for entry in st.session_state["items"]])
    st.divider()
    st.metric("Total energy", f"{totals.kcal:.0f} kcal")
    protein_col, carbs_col, fat_col = st.columns(3)
    protein_col.metric("Protein", f"{totals.protein_g:.1f} g")
    carbs_col.metric("Carbs", f"{totals.carbs_g:.1f} g")
    fat_col.metric("Fat", f"{totals.fat_g:.1f} g")

st.caption("PlateCheck · UI prototype · model integration pending")
