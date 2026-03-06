"use client";

interface DropdownParameters {
  label?: string;
  options: string[];
  optoval: any;
  value: string;
  onChange: (value: string) => void;
  iconUrl: string;
}

export default function Dropdown({
  label,
  options,
  optoval,
  value,
  onChange,
  iconUrl,
}: DropdownParameters) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
      {label && (
        <p style={{ fontSize: "0.9rem", fontWeight: "bold" }}>{label}</p>
      )}

      <div style={{ position: "relative", width: "fit-content" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "6px 12px",
            pointerEvents: "none",
          }}
          aria-hidden="true"
        >
          <img
            src={iconUrl}
            alt="dropdown menu"
            style={{ width: "24px", height: "24px", objectFit: "contain" }}
            className="theme-adaptive-icon"
          />
        </div>

        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          id={label}
          name={label}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            opacity: 0,
            cursor: "pointer",
            appearance: "none",
            WebkitAppearance: "none",
            MozAppearance: "none",
          }}
        >
          {options.map((option) => (
            <option key={option} value={option}>
              {optoval[option]}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
