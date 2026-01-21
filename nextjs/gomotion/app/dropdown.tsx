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
        <label style={{ fontSize: "0.9rem", fontWeight: "bold" }}>
          {label}
        </label>
      )}

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
