CREATE MIGRATION m1wpgl5l5vomhdfbzlbsud76nyxji4eq6mgc3swbwc4quvstzvtvta
    ONTO m1fiaroeeugctwstjbrywfe264a7hykjv6zxfcdfwor6zc7utwizyq
{
  ALTER TYPE default::WeatherData {
      DROP PROPERTY weather_description;
      DROP PROPERTY weather_main;
  };
};
