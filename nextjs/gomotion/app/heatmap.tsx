"use client";
import L from "leaflet";
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { scaleLinear } from "d3-scale";

const getColor = scaleLinear<string>()
  .domain([-3, 0, 3])
  .range(["#69298F", "#ca4679", "#FFD127"]);

export default function Heatmap({ geoData, zScores, barriSetter }: any) {
  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl;

    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
      iconUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
      shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
    });
  }, []);

  const style = (feature: any) => {
    return {
      fillColor:
        feature.properties.nom_barri in zScores
          ? getColor(zScores[feature.properties.nom_barri])
          : "#555",
      weight: 1,
      opacity: 1,
      color: "#888",
      dashArray: "1",
      fillOpacity: 0.9,
    };
  };

  const onEachFeature = (feature: any, layer: any) => {
    layer.on({
      //mouseover: highlightFeature,
      //mouseout: resetHighlight,
      click: () => barriSetter(feature.properties.nom_barri),
    });
  };

  return (
    <div className="heatmap">
      <MapContainer
        center={[41.4, 2.15]}
        zoom={11}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution="Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
          url={
            window.matchMedia("(prefers-color-scheme: dark)").matches //dark mode
              ? "https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png"
              : "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"
          }
        />
        <GeoJSON data={geoData} style={style} onEachFeature={onEachFeature} />
      </MapContainer>
    </div>
  );
}
