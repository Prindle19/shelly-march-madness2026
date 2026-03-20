# --- UNIFIED COLOR & GRAMMAR ENGINE ---
def get_stretched_gradient(val, mx, mid):
    """
    Unified 3-Point Gradient: Ice (#05FFFF) -> Neutral -> Fire (#FF0505).
    Ensures margin and cell colors use the same scale.
    """
    if val == mid:
        return "rgba(128, 128, 128, 0.2)", "inherit"
    
    if val > mid:
        # Scale between Neutral and Max Fire (#FF0505)
        ratio = (val - mid) / (mx - mid) if (mx - mid) > 0 else 0
        r = int(128 + (127 * ratio))
        g = int(128 - (123 * ratio))
        b = int(128 - (123 * ratio))
        # High contrast text flip
        txt = "white" if ratio > 0.4 else "black"
        return f"rgb({r}, {g}, {b})", txt
    else:
        # Scale between Min Ice (#05FFFF) and Neutral
        ratio = val / mid if mid > 0 else 0
        r = int(5 + (123 * ratio))
        g = int(255 - (127 * ratio))
        b = int(255 - (127 * ratio))
        # High contrast text flip
        txt = "white" if ratio < 0.6 else "black"
        return f"rgb({r}, {g}, {b})", txt

# --- IN THE GRID LOOP ---
# Grammar check for (1 Win) vs (2 Wins)
win_text = "Win" if wins == 1 else "Wins"
label = f"<br><span style='font-size: 0.65rem;'>({wins} {win_text})</span>" if wins > 0 else ""
