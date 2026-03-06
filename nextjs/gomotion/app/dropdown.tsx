"use client";

interface DropdownParameters {
  label?: string;
  options: string[];
  optoval: any;
  value: string;
  onChange: (value: string) => void;
}

export default function Dropdown({
  label,
  options,
  optoval,
  value,
  onChange,
}: DropdownParameters) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
      {label && (
        <p style={{ fontSize: "0.9rem", fontWeight: "bold" }}>{label}</p>
      )}

      <select
  value={value}
  onChange={(e) => onChange(e.target.value)}
  id={label}
  name={label}
  style={{
    appearance: "none",
    WebkitAppearance: "none",
    MozAppearance: "none",
    background: "none",

    padding: "6px 12px",
    width: "fit-content", // o "100%" si quieres que ocupe todo
    fontSize: "1rem",
  }}
>
        {options.map((option) => (
          <option key={option} value={option}>
            {optoval[option]}
          </option>
        ))}
      </select>
    </div>
  );
}