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
