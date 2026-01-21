"use client";

function Row()
{

}

export default function BarriInfo() {
  const columns: Array<string> = [];

  return (
    <div
      className="barriInfo"
      style={{
        backgroundColor: "yellow",
        display: "flex",
        flexDirection: "column",
        overflowX: "scroll",
      }}
    >
      <div style={{ width: "1000px" }}></div>
      <div style={{ overflowY: "scroll" }}></div>
    </div>
  );
}
