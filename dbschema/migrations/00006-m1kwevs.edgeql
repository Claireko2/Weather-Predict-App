CREATE MIGRATION m1kwevsnxdg6ko2ovuqet6prd7pjmz2xcmjiksfbgognvixnboxn2a
    ONTO m1hjozkkbnicyr6hew4qwacgj5mbgphnp3t66qtzrvx3mqnhglwgvq
{
  ALTER TYPE default::WeatherData {
      CREATE OPTIONAL PROPERTY predicted_rain_chance: std::float64;
  };
};
