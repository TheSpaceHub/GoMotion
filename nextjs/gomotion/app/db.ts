import { Pool } from "pg";

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT ? parseInt(process.env.DB_PORT) : 6543,
  database: process.env.DB_NAME,
  ssl: {
    rejectUnauthorized: false,
  },
});


export default pool;
