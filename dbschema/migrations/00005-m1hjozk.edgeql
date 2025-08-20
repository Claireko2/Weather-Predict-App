CREATE MIGRATION m1hjozkkbnicyr6hew4qwacgj5mbgphnp3t66qtzrvx3mqnhglwgvq
    ONTO m14aczel6fb5kiyx5mkxdq2ndpweeh3xh4nywya6ia5lvmeoeswesq
{
  ALTER TYPE default::WeatherData {
      CREATE PROPERTY rainfall: std::float32;
  };
};
