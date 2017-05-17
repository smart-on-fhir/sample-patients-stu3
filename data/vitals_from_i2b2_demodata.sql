select (case sd.patient_num 
WHEN	1000000108	THEN	1288992
WHEN	1000000071	THEN	2081539
WHEN	1000000096	THEN	1291938
WHEN	1000000018	THEN	1557780
WHEN	1000000025	THEN	2502813
WHEN	1000000119	THEN	1520204
WHEN	1000000083	THEN	644201
WHEN	1000000026	THEN	1272431
WHEN	1000000085	THEN	736230
WHEN	1000000011	THEN	1551992
WHEN	1000000043	THEN	2347217
WHEN	1000000076	THEN	1869612
WHEN	1000000101	THEN	665677
WHEN	1000000087	THEN	935270
WHEN	1000000082	THEN	765583
WHEN	1000000087	THEN	1137192
WHEN	1000000014	THEN	981968
WHEN	1000000075	THEN	2354220
WHEN	1000000031	THEN	1796238
WHEN	1000000063	THEN	2113340
WHEN	1000000111	THEN	621799
WHEN	1000000074	THEN	1577780
WHEN	1000000002	THEN	1540505
WHEN	1000000089	THEN	613876
WHEN	1000000049	THEN	1213208
WHEN	1000000022	THEN	967332
WHEN	1000000036	THEN	640264
WHEN	1000000028	THEN	1685497
WHEN	1000000093	THEN	2169591
WHEN	1000000097	THEN	1951076
WHEN	1000000006	THEN	629528
WHEN	1000000007	THEN	2042917
WHEN	1000000012	THEN	724111
WHEN	1000000041	THEN	897185
WHEN	1000000088	THEN	1186747
WHEN	1000000122	THEN	880378
WHEN	1000000065	THEN	1482713
ELSE -1
END
) as PID, sd.start_date as TIMESTAMP,  sd.start_date, sd.end_date, 'ambulatory' as encounter_type, heart_rate.v as heart_rate, respiratory_rate.v as respiratory_rate, temperature.v as temperature, weight.v as weight, height.v as height, bmi.v as bmi, systolic.v as systolic, diastolic.v as diastolic, oxygen_saturation.v as oxygen_saturation from (select start_date, end_date, patient_num from observation_fact where concept_cd in ('LOINC:8462-4','LOINC:8480-6','LOINC:8302-2','LOINC:39156-5','LOINC:8310-5','LOINC:3141-9','LOINC:8867-4','LOINC:2710-2','LOINC:9279-1')  group by start_date, end_date, patient_num) sd 
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:8462-4'  group by of1.patient_num, of1.start_date, of1.concept_cd) heart_rate on heart_rate.start_date=sd.start_date and heart_rate.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:9279-1'  group by of1.patient_num, of1.start_date, of1.concept_cd) respiratory_rate on respiratory_rate.start_date=sd.start_date and respiratory_rate.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:8480-6'  group by of1.patient_num, of1.start_date, of1.concept_cd) systolic on systolic.start_date=sd.start_date and systolic.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:8462-4'  group by of1.patient_num, of1.start_date, of1.concept_cd) diastolic on diastolic.start_date=sd.start_date and diastolic.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:8302-2'  group by of1.patient_num, of1.start_date, of1.concept_cd) height on height.start_date=sd.start_date and height.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:39156-5'  group by of1.patient_num, of1.start_date, of1.concept_cd) bmi  on bmi.start_date=sd.start_date and bmi.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:8310-5'  group by of1.patient_num, of1.start_date, of1.concept_cd) temperature on temperature.start_date=sd.start_date and temperature.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:3141-9'  group by of1.patient_num, of1.start_date, of1.concept_cd)  weight on weight.start_date=sd.start_date and weight.patient_num=sd.patient_num
join (select start_date, patient_num, max(nval_num) as v from observation_fact of1 where of1.concept_cd='LOINC:2710-2'  group by of1.patient_num, of1.start_date, of1.concept_cd) oxygen_saturation on oxygen_saturation.start_date=sd.start_date and oxygen_saturation.patient_num=sd.patient_num 
WHERE sd.patient_num in (1000000108,1000000071,1000000096,1000000018,1000000025,1000000119,1000000083,1000000026,1000000085,1000000011,1000000043,1000000076,1000000101,1000000087,1000000082,1000000087,1000000014,1000000075,1000000031,1000000063,1000000111,1000000074,1000000002,1000000089,1000000049,1000000022,1000000036,1000000028,1000000093,1000000097,1000000006,1000000007,1000000012,1000000041,1000000088,1000000122,1000000065) order by sd.patient_num, sd.start_date;
