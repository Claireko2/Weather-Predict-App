CREATE MIGRATION m1fiaroeeugctwstjbrywfe264a7hykjv6zxfcdfwor6zc7utwizyq
    ONTO m1sxw7qpaqxye2keh3lcypi6pppni2qz6gbuvxrdwjg5bke75oakiq
{
  ALTER TYPE default::WeatherData {
      CREATE REQUIRED PROPERTY feels_like: std::float32 {
          SET REQUIRED USING (<std::float32>{});
      };
      ALTER PROPERTY humidity {
          SET TYPE std::int16 USING (<std::int16>.humidity);
      };
      ALTER PROPERTY pressure {
          SET TYPE std::int16 USING (<std::int16>.pressure);
      };
  };
  ALTER TYPE default::WeatherData {
      DROP PROPERTY rainfall;
  };
  ALTER TYPE default::WeatherData {
      CREATE REQUIRED PROPERTY temp_max: std::float32 {
          SET REQUIRED USING (<std::float32>{});
      };
  };
  ALTER TYPE default::WeatherData {
      CREATE REQUIRED PROPERTY temp_min: std::float32 {
          SET REQUIRED USING (<std::float32>{});
      };
      ALTER PROPERTY temperature {
          SET TYPE std::float32;
      };
      CREATE REQUIRED PROPERTY weather_description: std::str {
          SET REQUIRED USING (<std::str>{});
      };
      CREATE REQUIRED PROPERTY weather_main: std::str {
          SET REQUIRED USING (<std::str>{});
      };
      CREATE REQUIRED PROPERTY wind_deg: std::int16 {
          SET REQUIRED USING (<std::int16>{});
      };
      CREATE REQUIRED PROPERTY wind_speed: std::float32 {
          SET REQUIRED USING (<std::float32>{});
      };
  };
};
