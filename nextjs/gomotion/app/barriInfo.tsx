"use client";

function classifyPeak(zscore: number) {
  if (zscore >= 1.5) return "Massive peak";
  if (zscore >= 1) return "Peak";
  return "No peak";
}

function Row(data: any) {
  console.log(data);
  return (
    <tr>
      <td>{data["barri"]}</td>
      <td>{Math.round(data["intensity"])}</td>
      <td>{Math.round(data["mean"])}</td>
      <td>{Math.round(data["density"])}</td>
      <td>{Math.round(100 * data["zscore"]) / 100}</td>
      <td>{classifyPeak(data["zscore"])}</td>
    </tr>
  );
}

export default function BarriInfo({ data }: any) {
  let rows: Array<any> = [];

  for (let i = 0; i < data["rows"].length; i++) {
    rows.push(Row(data["rows"][i]));
  }

  return (
    <div className="barriInfo">
      <table>
        <thead>
          <tr>
            <th>Barri</th>
            <th>Traffic</th>
            <th>Average</th>
            <th>Density</th>
            <th>Deviation</th>
            <th>Peak</th>
          </tr>
        </thead>
        <tbody>{...rows}</tbody>
      </table>
      <div style={{ overflowY: "scroll" }}></div>
    </div>
  );
}
