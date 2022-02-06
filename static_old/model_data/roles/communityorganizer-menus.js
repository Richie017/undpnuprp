

var menu_config = [
      {
          "icon": "fbx-report",
          "items": [
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/savings-and-credit/",
                          "order": 5,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "reports",
                                  "context": "SavingsAndCreditReport"
                              }
                          ],
                          "title": "Savings and Credit"
                      }
                  ],
                  "link": "",
                  "order": 2,
                  "title": "Savings & Credit"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/crmif-report/",
                          "order": 15,
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
                          "order": 20,
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
                  "order": 9,
                  "title": "SIF & CRMIF"
              }
          ],
          "link": "/pg-member-information-indicators/",
          "order": 0,
          "title": "Dashboard"
      },
      {
          "icon": "fbx-target",
          "items": [
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/sef-business-grantee/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "SEFBusinessGrantee"
                              }
                          ],
                          "title": "Business Grantees"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/sef-apprenticeship-grantee/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "SEFApprenticeshipGrantee"
                              }
                          ],
                          "title": "Apprenticeship Grantees"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/sef-education-dropout-grantee/",
                          "order": 3,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "SEFEducationDropoutGrantee"
                              }
                          ],
                          "title": "Education Grantees (Addressing Dropout)"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/sef-education-early-marriage-grantee/",
                          "order": 4,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "SEFEducationChildMarriageGrantee"
                              }
                          ],
                          "title": "Education Grantees (Early Child Marriage)"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/sef-nutrition-grantee/",
                          "order": 5,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "SEFNutritionGrantee"
                              }
                          ],
                          "title": "Nutrition Grantees"
                      }
                  ],
                  "link": "",
                  "order": 3,
                  "title": "Grantees"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/monthly-target/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "MonthlyTarget"
                              }
                          ],
                          "title": "Monthly Targets"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/monthly-progress/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "MonthlyProgress"
                              }
                          ],
                          "title": "Monthly Progress"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/quantitative-report/",
                          "order": 3,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "QuantitativeReport"
                              }
                          ],
                          "title": "Qualitative Report"
                      }
                  ],
                  "link": "",
                  "order": 4,
                  "title": "Target & Progress"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/training/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "Training"
                              }
                          ],
                          "title": "Trainings"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/workshop/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "Workshop"
                              }
                          ],
                          "title": "Workshops"
                      }
                  ],
                  "link": "",
                  "order": 6,
                  "title": "Training & Workshop"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/savings-and-credit-groups/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "SavingsAndCreditGroup"
                              }
                          ],
                          "title": "Savings & Credit Groups"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/primary-groups/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "PrimaryGroup"
                              }
                          ],
                          "title": "Primary Groups"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/cdc/",
                          "order": 3,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "CDC"
                              }
                          ],
                          "title": "CDC"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/cdc-cluster/",
                          "order": 4,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "CDCCluster"
                              }
                          ],
                          "title": "CDC Cluster"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/federation/",
                          "order": 5,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "Federation"
                              }
                          ],
                          "title": "Federation"
                      }
                  ],
                  "link": "",
                  "order": 7,
                  "title": "Community Organizations"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/housing-development-fund/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "CommunityHousingDevelopmentFund"
                              }
                          ],
                          "title": "Community Housing Development Fund"
                      }
                  ],
                  "link": "",
                  "order": 7,
                  "title": "Community Housing Development Fund"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/nutrition/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "Nutrition"
                              }
                          ],
                          "title": "Nutrition"
                      }
                  ],
                  "link": "",
                  "order": 8,
                  "title": "Nutrition"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/land-tenure-security/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "LandTenureSecurity"
                              }
                          ],
                          "title": "Land Tenure Security"
                      }
                  ],
                  "link": "",
                  "order": 9,
                  "title": "Land Tenure Security"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/operation-and-maintenance/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "OperationAndMaintenanceFund"
                              }
                          ],
                          "title": "Operation and Maintenance Fund"
                      }
                  ],
                  "link": "",
                  "order": 11,
                  "title": "Operation and Maintenance"
              }
          ],
          "link": "/primary-groups/",
          "order": 5,
          "title": "Entry"
      },
      {
          "icon": "fbx-alerts",
          "items": [
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/news/",
                          "order": 1000,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "core",
                                  "context": "News"
                              }
                          ],
                          "title": "News & Announcement"
                      }
                  ],
                  "link": "",
                  "order": 1,
                  "title": "News & Notifications"
              },
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/savings-and-credit-alert/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "nuprp_admin",
                                  "context": "SavingsAndCreditReportAlert"
                              }
                          ],
                          "title": "Single Alert CDC wise"
                      }
                  ],
                  "link": "",
                  "order": 3,
                  "title": "Savings and Credit Alerts"
              }
          ],
          "link": "/duplicate-id-alerts/",
          "order": 15,
          "title": "Alerts"
      },
      {
          "icon": "fbx-task",
          "items": [
              {
                  "items": [
                      {
                          "hide": false,
                          "items": [],
                          "link": "/pending-scg-monthly-report/",
                          "order": 1,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "PendingSCGMonthlyReport"
                              }
                          ],
                          "title": "Pending SCG Reports"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/approved-scg-monthly-report/",
                          "order": 2,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "ApprovedSCGMonthlyReport"
                              }
                          ],
                          "title": "Approved SCG Reports"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/pending-cdc-monthly-report/",
                          "order": 3,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "PendingCDCMonthlyReport"
                              }
                          ],
                          "title": "Pending CDC Reports"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/approved-cdc-monthly-report/",
                          "order": 4,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "ApprovedCDCMonthlyReport"
                              }
                          ],
                          "title": "Approved CDC Reports"
                      },
                      {
                          "hide": false,
                          "items": [],
                          "link": "/cumulative-reports/",
                          "order": 5,
                          "required-permission": [
                              {
                                  "access": 1,
                                  "app": "approvals",
                                  "context": "CumulativeReport"
                              }
                          ],
                          "title": "Cumulative Reports"
                      }
                  ],
                  "link": "",
                  "order": 1,
                  "title": "Savings & Credit Reports"
              }
          ],
          "link": "/pending-scg-monthly-report/",
          "order": 34,
          "title": "Approvals"
      }
  ];
var url_mapping = {
      "/approved-cdc-monthly-report/": "Approvals",
      "/approved-scg-monthly-report/": "Approvals",
      "/cdc-cluster/": "Entry",
      "/cdc/": "Entry",
      "/crmif-report/": "Dashboard",
      "/cumulative-reports/": "Approvals",
      "/federation/": "Entry",
      "/housing-development-fund/": "Entry",
      "/land-tenure-security/": "Entry",
      "/monthly-progress/": "Entry",
      "/monthly-target/": "Entry",
      "/news/": "Alerts",
      "/nutrition/": "Entry",
      "/operation-and-maintenance/": "Entry",
      "/pending-cdc-monthly-report/": "Approvals",
      "/pending-scg-monthly-report/": "Approvals",
      "/primary-groups/": "Entry",
      "/quantitative-report/": "Entry",
      "/savings-and-credit-alert/": "Alerts",
      "/savings-and-credit-groups/": "Entry",
      "/savings-and-credit/": "Dashboard",
      "/sef-apprenticeship-grantee/": "Entry",
      "/sef-business-grantee/": "Entry",
      "/sef-education-dropout-grantee/": "Entry",
      "/sef-education-early-marriage-grantee/": "Entry",
      "/sef-nutrition-grantee/": "Entry",
      "/sif-report/": "Dashboard",
      "/training/": "Entry",
      "/workshop/": "Entry"
  };

