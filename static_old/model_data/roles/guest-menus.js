

var menu_config = [
      {
          "icon": "fbx-report",
          "items": [
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/urban-governance-and-planning-report/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "UrbanGovernanceAndPlanningReport"
                              }
                          ],
                          "title": "Planning and Urban Governance"
                      }
                  ],
                  "link": "",
                  "order": 1,
                  "title": "Planning and Urban Governance "
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/pg-member-information-indicators/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "PGMemberInformationReport"
                              }
                          ],
                          "title": "PG Member Information"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/pg-hh-head-information-indicators/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "PGHHHeadInformationReport"
                              }
                          ],
                          "title": "PG HH Head Information"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/pg-hh-information-indicators/",
                          "order": 3,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "PGHHInformationReport"
                              }
                          ],
                          "title": "PG HH Information"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/socio-economic-fund-grant-indicators/",
                          "order": 4,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "SocioEconomicFundGrantReport"
                              }
                          ],
                          "title": "Socio Economic Fund Grant"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/economic-development-and-livelihood-report/",
                          "order": 5,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "EconomicDevelopmentAndLivelihood"
                              }
                          ],
                          "title": "Gender"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/nutrition-report/",
                          "order": 6,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "NutritionReport"
                              }
                          ],
                          "title": "Nutrition"
                      }
                  ],
                  "link": "",
                  "order": 3,
                  "title": "Local Economy Livelihood and Financial Inclusion "
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/climate-housing-development-fund/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "ClimateHousingDevelopmentFundReport"
                              }
                          ],
                          "title": "Climate Housing Development Fund"
                      }
                  ],
                  "link": "",
                  "order": 4,
                  "title": "Housing Finance "
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/crmif-report/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "CRMIFReport"
                              }
                          ],
                          "title": "CRMIF"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/sif-report/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "SIFReport"
                              }
                          ],
                          "title": "SIF"
                      }
                  ],
                  "link": "",
                  "order": 5,
                  "title": "Infrastructure & Urban Services "
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/hh-survey-indicators/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "HouseholdSurveyIndicatorReport"
                              }
                          ],
                          "title": "Household Survey Indicators"
                      }
                  ],
                  "link": "",
                  "order": 7,
                  "title": "Household Information"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/survey-location-map/",
                          "order": 3,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "SurveyLocationReport"
                              }
                          ],
                          "title": "HH Survey Location"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/pg-member-location-map/",
                          "order": 4,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "PGMemberLocationReport"
                              }
                          ],
                          "title": "PG Member Registration Location"
                      }
                  ],
                  "link": "",
                  "order": 11,
                  "title": "Maps"
              }
          ],
          "link": "/pg-member-information-indicators/",
          "order": 0,
          "title": "Dashboard"
      }
  ];
var url_mapping = {
      "/climate-housing-development-fund/": "Dashboard",
      "/crmif-report/": "Dashboard",
      "/economic-development-and-livelihood-report/": "Dashboard",
      "/hh-survey-indicators/": "Dashboard",
      "/nutrition-report/": "Dashboard",
      "/pg-hh-head-information-indicators/": "Dashboard",
      "/pg-hh-information-indicators/": "Dashboard",
      "/pg-member-information-indicators/": "Dashboard",
      "/pg-member-location-map/": "Dashboard",
      "/sif-report/": "Dashboard",
      "/socio-economic-fund-grant-indicators/": "Dashboard",
      "/survey-location-map/": "Dashboard",
      "/urban-governance-and-planning-report/": "Dashboard"
  };

