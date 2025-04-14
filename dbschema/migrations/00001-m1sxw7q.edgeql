CREATE MIGRATION m1sxw7qpaqxye2keh3lcypi6pppni2qz6gbuvxrdwjg5bke75oakiq
    ONTO initial
{
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::WeatherData {
      CREATE REQUIRED PROPERTY city: std::str;
      CREATE REQUIRED PROPERTY humidity: std::float64;
      CREATE REQUIRED PROPERTY pressure: std::float64;
      CREATE REQUIRED PROPERTY rainfall: std::float64;
      CREATE REQUIRED PROPERTY temperature: std::float64;
      CREATE REQUIRED PROPERTY timestamp: std::datetime;
  };
};
