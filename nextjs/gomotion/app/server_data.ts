"use server";
import pool from "./db";
import { QueryResult } from "pg";

export async function getMapData(day: any) {
  const result: QueryResult<any> = await pool.query(
    `
    with z as
    (select barri, stddev_samp(intensity) as std, avg(intensity) as mean
    from display_data
    group by barri)
    select d.barri, d.intensity, (d.intensity - z.mean) / z.std as zscore
    from display_data d, z
    where d.day = $1 and z.barri = d.barri
    `,
    [day]
  );
  return result.rows;
}

export async function getWeeklyTraffic(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT AVG(intensity), EXTRACT(ISODOW FROM DATE(day)) AS dotw
    FROM display_data
    WHERE barri=$1
    GROUP BY dotw ORDER BY dotw
    `,
    [barri]
  );
  return result.rows;
}

export async function getMonthlyTraffic(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT AVG(intensity), EXTRACT(MONTH FROM DATE(day)) AS month
    FROM display_data
    WHERE barri=$1
    GROUP BY month ORDER BY month
    `,
    [barri]
  );
  return result.rows;
}

export async function getAverageEventImpact(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT e.category, AVG(d.intensity)
    FROM display_data d, events e
    WHERE d.barri=$1 and d.day = e.day
    GROUP BY e.category
    `,
    [barri]
  );
  return result.rows;
}

export async function getRainIntensityCorrelation(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT m."precipitation_sum (mm)" AS rain, d.intensity, d.day
    FROM display_data d, meteo m
    WHERE d.barri=$1 and DATE(d.day) = m.day
    `,
    [barri]
  );
  return result.rows;
}

export async function getWorkdayVsHoliday(barri: string) {
  const result: QueryResult<any> = await pool.query(
    `
    SELECT intensity, is_holiday
    FROM display_data 
    WHERE barri=$1
    `,
    [barri]
  );
  return result.rows;
}

export async function getIntensityPerArea() {
  const result: QueryResult<any> = await pool.query(`
    SELECT g.nom_barri, g.superficie, AVG(d.intensity)
    FROM geospatial_data g, display_data d
    WHERE g.nom_barri = d.barri
    GROUP BY g.nom_barri, g.superficie
    `);
  return result.rows;
}
