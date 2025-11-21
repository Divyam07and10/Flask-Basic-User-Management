# Customer Location: Hover Tooltip and US States Integration

This README documents the lines of code that were added or modified to implement the on-hover, two-line tooltip for US states on the map, and how/why each piece exists. File paths referenced below:

- Component: `frontend/src/modules/customers/Location/index.js`
- Styles: `frontend/src/modules/customers/Location/style.js`

## Overview of What Was Added

- Load and render the US states GeoJSON onto the Google Map via `map.data.addGeoJson(...)`.
- Style each state polygon using `highlightedStates` color mapping.
- Show a Tooltip (two lines: Timezone, Time) after a short hover delay over an allowed state.
- Determine allowed states using the in-memory GeoJSON object returned by `Service.getUSStates()` (no network fetch on hover).
- Keep all tooltip visuals in a single CSS class (`classes.tooltip`) rather than inline styles.

---

## index.js: Map and Hover Logic

### 1) US States loading and styling

Location: `onMapLoad` callback in `CustomerLocation`.

```js
(async () => {
  const { data } = await Service.getUSStates();
  const usStatesData = data;
  map.data.addGeoJson(usStatesData);

  map.data.setStyle((feature) => {
    const stateName = feature.getProperty("name");
    const fillColor = highlightedStates[stateName] || "transparent";
    return {
      fillColor,
      fillOpacity: 0.5,
      strokeColor: "#000",
      strokeOpacity: 0.8,
      strokeWeight: 1,
    };
  });
  // ...
})();
```

- `Service.getUSStates()` returns a GeoJSON FeatureCollection. We store it in `usStatesData` for later checks.
- `map.data.addGeoJson(usStatesData)` injects the polygons into the map's Data Layer.
- `map.data.setStyle(...)` styles polygons with:
  - `fillColor`: from `highlightedStates[stateName]` if present, else transparent.
  - `fillOpacity`: 0.5 to keep the base map visible.
  - `strokeColor`, `strokeOpacity`, `strokeWeight`: subtle borders so the state outlines remain visible at various zooms.

### 2) Hover state utilities

```js
const clearHoverTimer = () => {
  if (hoverTimerRef.current) {
    clearTimeout(hoverTimerRef.current);
    hoverTimerRef.current = null;
  }
};

const hideHoverInfo = () => {
  clearHoverTimer();
  setState((prev) => ({
    ...prev,
    showingHoverInfoWindow: false,
    hoverInfoWindowPosition: null,
    hoverTimezone: "",
    hoverTime: "",
  }));
};
```

- `clearHoverTimer`: Ensures we never have multiple pending hover timers when the user moves the mouse quickly across the map.
- `hideHoverInfo`: Hides the tooltip and resets related fields whenever the cursor leaves a state.

### 3) Hover handler and allowlist + timezone fetch

```js
const handleStateHover = async (evt) => {
  const feature = evt.feature;
  const stateName = feature?.getProperty("name");
  const isAllowed = Array.isArray(usStatesData?.features)
    ? usStatesData.features.some((f) => {
        const n = f?.properties?.name;
        return (
          typeof n === "string" &&
          typeof stateName === "string" &&
          n.toLowerCase() === stateName.toLowerCase()
        );
      })
    : true;
  if (!isAllowed) return;

  const pos = evt.latLng?.toJSON ? evt.latLng.toJSON() : null;
  if (!pos) return;

  clearHoverTimer();
  hoverTimerRef.current = setTimeout(async () => {
    const timestamp = Math.floor(Date.now() / 1000);
    const url = `https://maps.googleapis.com/maps/api/timezone/json?location=${pos.lat},${pos.lng}&timestamp=${timestamp}&key=${googleMapsConfig.googleMapsApiKey}`;

    try {
      const tzRes = await fetch(url);
      const tzData = await tzRes.json();
      const ok = tzData.status === "OK";
      const tzId = ok ? (tzData.timeZoneId || tzData.timeZoneName) : null;
      const tzName = ok ? (tzData.timeZoneName || tzData.timeZoneId) : null;
      const timeStr = tzId
        ? new Intl.DateTimeFormat("en-US", {
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
            timeZone: tzId,
          }).format(new Date())
        : "";

      if (tzName) {
        setState((prev) => ({
          ...prev,
          showingHoverInfoWindow: true,
          hoverInfoWindowPosition: pos,
          hoverTimezone: tzName,
          hoverTime: timeStr,
        }));
      }
    } catch (_) {
      setState((prev) => ({
        ...prev,
        showingHoverInfoWindow: false,
      }));
    }
  }, 1000);
};

map.data.addListener("mouseover", handleStateHover);
map.data.addListener("mouseout", hideHoverInfo);
```

- `stateName`: We read the `name` property of the hovered state polygon.
- `isAllowed`: Checks the in-memory `usStatesData.features` for a case-insensitive match on `properties.name`. Using the already-loaded object avoids additional network requests and any caching complications.
- `pos`: Uses the mouse event’s `latLng` to place the tooltip.
- Debounce (1000ms): Reduces noise from brief, accidental hovers; the tooltip shows only when the user truly pauses over a state.
- Timezone API call:
  - `timeZoneId`/`timeZoneName` from Google Time Zone API.
  - Formats a human-friendly local time in that timezone.
- On success: Sets `showingHoverInfoWindow`, `hoverInfoWindowPosition`, `hoverTimezone`, and `hoverTime` to render the tooltip.
- On error: Hides the tooltip so we never show partial or incorrect values.

### 4) Tooltip rendering

Location: Inside the main `<GoogleMap>` render, wrapped by an `OverlayView` anchored at the hovered coordinates.

```jsx
{state.showingHoverInfoWindow && state.hoverInfoWindowPosition && (
  <OverlayView
    position={state.hoverInfoWindowPosition}
    mapPaneName={OverlayView.OVERLAY_MOUSE_TARGET}
  >
    <Tooltip
      open
      arrow
      placement="top"
      classes={{ tooltip: classes.tooltip }}
      disableFocusListener
      disableHoverListener
      disableTouchListener
      title={
        <div>
          <div>Timezone: {state.hoverTimezone}</div>
          <div>Time: {state.hoverTime}</div>
        </div>
      }
    >
      <div />
    </Tooltip>
  </OverlayView>
)}
```

- `OverlayView`: Provides a DOM anchor at the exact `lat/lng` for consistent tooltip placement directly over the hovered point.
- `Tooltip` from Material-UI:
  - `open`, `arrow`, `placement="top"`: Always show it (controlled), with an arrow pointing to the anchor, above the point.
  - `classes={{ tooltip: classes.tooltip }}`: Use a single, centralized style class.
  - `disable*Listener` props: Ensures the Tooltip is controlled by our map hover logic rather than internal MUI hover/focus tracking.
  - `title`: Two-line content—the only information required.
  - Child `<div />`: Invisible anchor element required by the Tooltip for positioning.

---

## style.js: Single Tooltip Class

```js
const useStyles = makeStyles((theme) => ({
  // ...other styles...
  tooltip: {
    backgroundColor: "#fff",
    color: "#000",
    fontFamily: "Roboto, Arial, sans-serif",
    fontSize: 13, // (Note: user adjusted to 12 in latest changes.)
    lineHeight: 1.3, // (Note: user adjusted to 1.2 in latest changes.)
  },
}));
```

- All tooltip visuals are centralized into a single class to satisfy the “use only style file” requirement and keep the component clean.
- Minimal properties:
  - `backgroundColor` and `color`: Matches the requested contrast (white on black text earlier; currently black text on white bg).
  - `fontFamily`, `fontSize`, `lineHeight`: Enforces consistent typography for both content lines.
- You later tuned the values to `fontSize: 12` and `lineHeight: 1.2`, which the component picks up automatically.

---

## Why These Choices

- Using `Service.getUSStates()` GeoJSON directly avoids extra fetches, cache headers, and race conditions on hover.
- Debounced hover avoids flicker and excessive API calls while still feeling responsive.
- Controlled Material-UI Tooltip inside a Google Maps `OverlayView` gives precise positioning and a simple render path.
- Centralizing all tooltip styles in `style.js` preserves separation of concerns and eliminates inline CSS.

---

## What Was Intentionally Not Done

- No state name placeholder is shown before timezone resolves, as per your guidance—only the intended two lines appear after the delay.
- No client-side caching layer for `usStates.json`; we rely on the in-memory GeoJSON object loaded once at map init.
- No extra/unrelated CSS classes: we collapsed to a single `tooltip` class.

---

## Touchpoints Summary

- `index.js`
  - `onMapLoad`: add/stylize states, set up hover listeners.
  - `handleStateHover`: debounce + timezone fetch + state updates.
  - Tooltip JSX: `OverlayView` + `Tooltip` with single style class.
- `style.js`
  - `tooltip`: one class to style the tooltip surface and text.

If you want this README to include screenshots or a quick troubleshooting section (e.g., missing Google Maps key, network errors), I can add that too.
