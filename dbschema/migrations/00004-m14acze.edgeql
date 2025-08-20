CREATE MIGRATION m14aczel6fb5kiyx5mkxdq2ndpweeh3xh4nywya6ia5lvmeoeswesq
    ONTO m1wpgl5l5vomhdfbzlbsud76nyxji4eq6mgc3swbwc4quvstzvtvta
{
  ALTER TYPE default::WeatherData {
      ALTER PROPERTY timestamp {
          SET TYPE std::str USING (<std::str>.timestamp);
      };
  };
};
