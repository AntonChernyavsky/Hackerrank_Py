/*
 * �������� ������� cust.personal_account_td
 * [�������-������ ������ cust.terminal_device � cust.personal_account]
 *
 * ��������� ����� �������:
 * <app_n, effective_from, effective_to, acc_id >
 *  	
 * �� ���� (app_n, effective_from) - ����. �� ��-�� ������ � effective-�������������
 * ��� ����� ���� �� ���. ������� ������ �������������� ���� _row_id, ������� �������� ������
 * � ������ �� (app_n, effective_from)
 *
 * ��������� ��������� appa_<...>.Z � ����������� �� ��������� � ����������
 * �� ������ ���������� ��������.
 *
 * ��������� �� ������ ���������� �������� �������� � ������� MTS_DETL.LAST_APPA.
 *
 * ������ �.�.
 */
 
%let DWL_PROCESS_NAME = appa;
 
/* �������������� �������� "������ ��������". ���� ���������� � 1, ��
 * ����������� ��������� � ������� ������� �� ��� �������, � �� �
 * ����������� � ������� ���������� ��������.
 */
%let DWL_FIRST_LOAD = %sysget(DWL_FIRST_LOAD);
 
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\ErrorControl.sas ****/
*#if 0;
*#endif;
 
/*������ %symexist �.�. �� �������� ������ ������� � 9 ������*/
%macro mSymExist(mvVariableName, mvSymExist);
    option noserror;
    data _NULL_;
        length s k $255;
        s = "&&&mvVariableName";
        k = '&' || "&mvVariableName";
        call symput("&mvSymExist", k=s);
    run;
    option serror;
%mend;
 
 
/* ��������� ���������� ����� � ���. */
%macro DWL_SILENT ;
    option nonotes nomprint nomlogic nosymbolgen;
    %global DWL_SILENT_NESTING_COUNTER;
 
    %local DWL_SILENT_NESTING_COUNTER_NOXST;
    %let DWL_SILENT_NESTING_COUNTER_NOXST = ;
 
    %mSymExist(DWL_SILENT_NESTING_COUNTER, DWL_SILENT_NESTING_COUNTER_NOXST);
    %if &DWL_SILENT_NESTING_COUNTER_NOXST %then
	    %let DWL_SILENT_NESTING_COUNTER = 0; /* ������� ������������ DWL_SILENT */
    %let DWL_SILENT_NESTING_COUNTER = %eval(&DWL_SILENT_NESTING_COUNTER + 1);
 
%mend DWL_SILENT;
 
/* �������� �������� DWL_SILENT. */
%macro DWL_END_SILENT(mvForce=0) ;
    %let DWL_SILENT_NESTING_COUNTER = %eval(&DWL_SILENT_NESTING_COUNTER - 1);
 
    %if &DWL_SILENT_NESTING_COUNTER <= 0 or &mvForce %then %do;
        %let DWL_SILENT_NESTING_COUNTER = 0;
        /* ������������ ��������������� ��������������� �� ���������
           �������� ����� � DWL_START_LOADING (�� ������ ������ ���� �������). */
        %local opts;
        %let opts = ;
        %if &DWL_MLOGIC %then %let opts = &opts mlogic;
        %if &DWL_MPRINT %then %let opts = &opts mprint;
        %if &DWL_SYMBOLGEN %then %let opts = &opts symbolgen;
        option notes &opts ;
    %end;
%mend DWL_END_SILENT;
 
 
/* One-time �������������, ���������� � ������ ��������. */
%macro DWL_START_LOADING ;
    option nonotes;
    proc optsave out=dwl_options; run;
 
    %DWL_SILENT ;
 
    %global DWL_INIT_TERM_NESTING_COUNTER
            DWL_HALTED DWL_STARTED_LOADING ;
    %let DWL_INIT_TERM_NESTING_COUNTER = 0; /* ������� ����������� DWL_INIT */
    %let DWL_HALTED = 0; /* ������� ���������� ���������� �������� */
    %let DWL_STARTED_LOADING = 1;
 
    %local DWL_PROCESS_NAME_NOXST;
    %let DWL_PROCESS_NAME_NOXST = ;
 
    %mSymExist(DWL_PROCESS_NAME, DWL_PROCESS_NAME_NOXST);
    %if &DWL_PROCESS_NAME_NOXST %then %do;
        %DWL_RAISE_ERROR("You must specify DWL_PROCESS_NAME!");
        %DWL_END_SILENT(mvForce=1);
    %end;
 
    * XXX ��������� ������� ./logs ;
	%local DWL_TEMP_LOG_NOXST;
    %let DWL_TEMP_LOG_NOXST = ;
	%mSymExist(DWL_TEMP_LOG, DWL_TEMP_LOG_NOXST);
 
	*�����, ���� ������ ��������� ��� - ��� �������� �����, ��� ������������ �����;
	%if &DWL_TEMP_LOG_NOXST %then %do;
		%global DWL_TEMP_LOG;				
	    %local mvStartDateTime mvStartTime;
	    %let mvStartDateTime = %sysfunc(datetime(), 18.);
	    %let mvStartTime = %sysfunc(timepart(&mvStartDateTime), 18.);
 
		%let DWL_TEMP_LOG = %sysfunc(pathname(work))/temp-log-%sysfunc(datepart(&mvStartDateTime), YYMMDD10.)-%sysfunc(hour(&mvStartTime), Z2.)%sysfunc(minute(&mvStartTime), Z2.)%sysfunc(second(&mvStartTime), Z2.).log;
	%end;
 
    /* ��� DWL_END_SILENT */
    %global DWL_MPRINT DWL_MLOGIC DWL_SYMBOLGEN;
    proc sql noprint;
        select OPTVALUE into :DWL_MPRINT from dwl_options where OPTNAME="MPRINT";
        select OPTVALUE into :DWL_MLOGIC from dwl_options where OPTNAME="MLOGIC";
        select OPTVALUE into :DWL_SYMBOLGEN from dwl_options where OPTNAME="SYMBOLGEN";
        drop table dwl_options;
    quit;
 
%EXIT:
    %DWL_END_SILENT;
%mend DWL_START_LOADING;
 
/* ��������������� ������ �� ��������� ��� ��� ����������� ������� � DWL_TERM.
   ���������� � ������ ������� �������. */
%macro DWL_INIT ;
    %DWL_SILENT;
 
    %local DWL_STARTED_LOADING_NOXST;
    %let DWL_STARTED_LOADING_NOXST = ;
 
    %mSymExist(DWL_STARTED_LOADING, DWL_STARTED_LOADING_NOXST);
    %if &DWL_STARTED_LOADING_NOXST %then %do;
        %DWL_RAISE_ERROR (You must call DWL_START_LOADING before DWL_INIT!);
    %end;
 
    %let DWL_INIT_TERM_NESTING_COUNTER = %eval(&DWL_INIT_TERM_NESTING_COUNTER + 1);
    %IF &DWL_INIT_TERM_NESTING_COUNTER NE 1 %THEN %GOTO EXIT;
 
    %local DWL_NOCHECKLOG_NOXST;
    %let DWL_NOCHECKLOG_NOXST = ;
	%mSymExist(DWL_NOCHECKLOG, DWL_NOCHECKLOG_NOXST);
 
    /* ����� ������� ����� DWL_INIT �������� ������ � ��������� ���,
       ������� ������������ ����������� �������� DWL_TERM �� �������
       ������� ������.*/
    %if &DWL_NOCHECKLOG_NOXST %then %do;	
		PROC PRINTTO LOG = "&DWL_TEMP_LOG" NEW; RUN;
	%end;
%EXIT:
    %DWL_END_SILENT;
%mend DWL_INIT;
 
/* ������ ����, ���������� ���������, ��������� DWL_INIT �� ������� ������� ������.
   �����, ����� �������� ������, �� �������� �� SYSRC/SYSERR.
   ���������� � ����� ������� �������. */
%macro DWL_TERM ;
    %DWL_SILENT;
 
    %LET DWL_INIT_TERM_NESTING_COUNTER = %EVAL (&DWL_INIT_TERM_NESTING_COUNTER - 1);
    %IF &DWL_INIT_TERM_NESTING_COUNTER NE 0 %THEN %GOTO EXIT;
 
    %LOCAL DWL_STOP_TIME;
    %LET DWL_STOP_TIME = %SYSFUNC(DateTime());
 
    %local DWL_NOCHECKLOG_NOXST;
	%let DWL_NOCHECKLOG_NOXST = ;
 
	%mSymExist(DWL_NOCHECKLOG, DWL_NOCHECKLOG_NOXST);
    %if &DWL_NOCHECKLOG_NOXST %then %do;
        PROC PRINTTO LOG = LOG; RUN;
 
        FILENAME DWL_LOG "&DWL_TEMP_LOG";
 
        DATA _null_;
            LENGTH line $ 200;
 
            INFILE DWL_LOG TRUNCOVER; INPUT line 1-200;
 
            IF Substr (line, 1, 5) eq 'ERROR' THEN DO;
                idx = Index (line, ':');
 
                IF idx THEN DO;
                    CALL SYMPUT('DWL_HALTED', '1');
                    PUT "ERROR: Error message found in log"; /*%sysfunc(dequote(&DWL_TEMP_LOG))";*/ /*���������������� ����� ������ � SAS v.8 ��� v.9 ��� ����� ����������������*/
                END;
            END;
    /* ���� �� ��������� �� warnings
            IF Substr (line, 1, 7) eq 'WARNING' AND  NOT INDEX(line, 'will expire within') THEN DO;
            END;
    */
        RUN;
 
		%local DWL_DUMP_LOG_NOXST;
		%let DWL_DUMP_LOG_NOXST = ;
 
		%mSymExist(DWL_DUMP_LOG, DWL_DUMP_LOG_NOXST);
		%if not &DWL_DUMP_LOG_NOXST %then
 
		%do;
			data _NULL_;
				FILE "&DWL_DUMP_LOG" MOD;
 
				INFILE "&DWL_TEMP_LOG" end = end1;
				do while(not end1);
					INPUT;
					PUT _infile_;
				end;
 
				stop;
			run;
		%end;
    %end;
 
%EXIT:
    %DWL_END_SILENT;
%mend DWL_TERM;
 
/* ������� ��������� �� ������ � �������� ��������� ������ ��������
 * (��� ������� ����������� ������������� DWL_NOT_OK ���������� �����).
 */
%macro DWL_RAISE_ERROR (mvMessage) ;
     %let DWL_HALTED = 1;
     %put ERROR: %sysfunc(dequote(&mvMessage));
%mend DWL_RAISE_ERROR;
 
/* �������� �� ������. ������������ ��������� �������:
 *    %if %DWL_NOT_OK %then %goto EXIT;
 * ��� EXIT - ����� � ����� �������
 */
%macro DWL_NOT_OK ;
    %if (&DWL_HALTED ne 1) and (%eval(&sysrc)>4 or %eval(&syserr)>4) %then %do;
        /* ���� ��������� ������, ������������� ���� ���������� ����������. */
        %let DWL_HALTED = 1;
    %end;
 
    (&DWL_HALTED eq 1)
%mend DWL_NOT_OK;
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\ErrorControl.sas ****/
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\dwh\region\common\mCreateDiffTransport.sas ****/
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\RegLoadInitialization.sas ****/
/**
 * ��������������� ������� ��� ������������ ��������:
 * mGetLoadParams � mMarkSuccessfulLoad.
 *
 * NOTE: ������� ������ �������� � SASv8! (��� ������������ ��������)
 *
 * 27.06.2008 ������ ���������
 * 19.12.2008 �. ���������  -- ���������.
 */
 
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\LoadInitialization.sas ****/
/**
 * ������������� ��������������� DWL_LOAD_ID (������������� ��������).
 * ���������� � ������ ��������. ���������� ���������� DWL_PROCESS_NAME
 * ��� ����������� ����� ��������.
 *
 * ������ �������� �������� � MTS_LOGS.LOADS_LOG. ��������� LOAD_ID
 * ����������� ��� max(load_id)+1 ��� 60000, ���� ���� �� ����������
 * (����� ID ����� ��������� �� ������������ � ID ������, ������������
 * ������ ������������������).
 *
 * NOTE: ������� ������ �������� � SASv8! (��� ������������ ��������)
 *
 * ������ ���������   27.06.2008
 * ������� ���������  6.08.2008
 */
 
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\mTryLock.sas ****/
/**
 * ���������� �������� ������� member (���� LIBNAME.MEMNAME).
 * ������� ������ ������������. ���� �� ��������� ����������
 * ������� ������� �������� �� �������, ����� ��������� �� ������
 * � ������������� ���� ������, ������� ����� ������������
 * �������� DWL_NOT_OK.
 *
 * ����� �� ������ ����� �������� ��� ��������
 *  lock &mvTable clear;
 *
 * ���������:
 *    mvTable - ��� �������, ����������� � ��������� libname.
 *    mvTimeout - ������� � ��������, �� ��������� ��������
 *                ����� � ������� (������� mvRetryPeriod).
 *    mvRetryPeriod - ���� �� ������� �������� �������,
 *                    ��������� ������� ������������ �����
 *                    ��� ����� ������.
 *
 * � ���������, ���������� �����������, ��� ���� ��� ��������
 * ����������, ������ ������ ����� ������ � ���. ��� ������� �
 * ���, ��� ���� �� ������ ��������� ����� � ��� (-altlog) � lock
 * statement'�. ������ ���� "ERROR: You cannot lock <xxx.yyy>.DATA
 * because <xxx.yyy>.DATA is in use by user ZZZ." ���� ������������
 * ��� ������� �����.
 *
 * ��. http://www.lexjansen.com/pharmasug/2005/posters/po33.pdf
 */
%macro mTryLock(mvTable, mvTimeout=10, mvRetryPeriod=1);
	%local mvStartTime;
	%let mvStartTime = %sysfunc(datetime());
 
	%if "%scan(&mvTable, 2, .)" = "" %then %do;
		%DWL_RAISE_ERROR("Invalid parameter mvTable: expected <libname>.<memname>, got &mvTable");
		%goto EXIT;
	%end;
 
	/* ���� ����� �� ������ race ����� ����� �������� mTryLock: ��� �����
	 * ������� ���������� ������ data step, �� ������ ���� ������ �������
	 * �������� �������. ������ ����� ������ ��������� � ����������� ����
	 * �����. */
	%do %until(&syslckrc <= 0 or
				%sysevalf(%sysfunc(datetime()) > (&mvStartTime + &mvTimeout)));
		/* ������ �������� ������� ������� (����� ��������� ����� � ����). */
		data _null_;
			put "NOTE: Trying to open and lock &mvTable....";
			dsid = 0;
			*rc = sleep(1); /* ��� ����� �� ������������� ��� ����� */
			do until (dsid > 0 or datetime() > (&mvStartTime + &mvTimeout));
				dsid = open("&mvTable");
				if (dsid = 0) then rc = sleep(&mvRetryPeriod, 1);
			end;
			if (dsid > 0) then rc = close(dsid);
		run;
 
		lock &mvTable;
		%if &syslckrc > 0 %then %do; /* �� ������� �������� ���. */
			%local rc; %let rc = %sysfunc(sleep(1, 1));
		%end;
	%end;
 
	%if &syslckrc > 0 %then %do; /* �� ������� �������� ���. */
		%DWL_RAISE_ERROR("Timerout (&mvTimeout seconds) exceeded trying to acquire a lock on &mvTable..");
	%end;
 
%EXIT:
%mend mTryLock;
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\mTryLock.sas ****/
 
%macro DWL_LOAD_ID_INIT;
    %DWL_INIT;
 
    %global DWL_LOAD_ID DWL_LOAD_START_DTTM;
 
	%let DWL_LOAD_START_DTTM = %sysfunc(datetime(), 18.);
    %if not %sysfunc(exist(mts_logs.loads_log)) %then %do;
        data mts_logs.loads_log ;
            attrib
              load_id         length=8    label="������������� ��������"
              process_name    length=$50  label="�������� ��������"
              load_start_dttm length=6    label="����-����� ������ ������ ��������" format=DATETIME.
			  /*status		  length=$4	  label="��������� ���������� �������� (DONE ��� ������� �������������)"*/
            ;
            load_id=.;process_name="";load_start_dttm=.;/* SASv8 �� ������������ call missing. */
            delete;
        run;
	    %if %DWL_NOT_OK %then %goto EXIT;
    %end;
 
	%mTryLock(mts_logs.loads_log);
    %if %DWL_NOT_OK %then %goto EXIT;
 
    proc sql noprint;
		select coalesce(max(load_id)+1, 60000) format 18. into :DWL_LOAD_ID
			from mts_logs.loads_log;
    quit;
    %if %DWL_NOT_OK %then %goto EXIT;
 
	/* ����������� �� ������ ��������. */
	%let DWL_LOAD_ID = %eval(&DWL_LOAD_ID+0);
 
    proc sql;
        insert into mts_logs.loads_log
          set load_id = &DWL_LOAD_ID,
              process_name = "&DWL_PROCESS_NAME",
              load_start_dttm = &DWL_LOAD_START_DTTM;
    quit;
    %if %DWL_NOT_OK %then %goto EXIT;
 
	lock mts_logs.loads_log clear;
    %if %DWL_NOT_OK %then %goto EXIT;
 
%EXIT:
    %DWL_TERM;
%mend DWL_LOAD_ID_INIT;
 
/**
 * ���������� �� ���������� ������ ��������.
 */
/* TODO: ����� ���� �� �������� � mGenerateScript � ���������� ���������� ������ ���� ���������.
%macro DWL_FINISHED_LOADING;
	%if not %DWL_NOT_OK %then %do;
		proc sql;
			update mts_logs.loads_log
				set status="DONE"
				where load_id = &DWL_LOAD_ID;
		quit;
	%end;
%mend DWL_FINISHED_LOADING;
*/
 
%macro mTest_LOAD_INIT;
	%include "&SVNROOT\common\ErrorControl.sas";
	%let DWL_PROCESS_NAME=test; %let DWL_NOCHECKLOG=1;
	%DWL_START_LOADING;
 
 
 
	%symdel DWL_LOAD_ID;
	%DWL_LOAD_ID_INIT;
 
	%put "&DWL_LOAD_ID";
	%*DWL_FINISHED_LOADING;
 
%mend mTest_LOAD_INIT;
 
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\LoadInitialization.sas ****/
 
%global DWL_LOAD_ID;
%global DWL_LOAD_FROM;
%global DWL_LOAD_TILL;
 
%let DWL_REGLOADS_LOG = mts_logs.loads_ba_status;
 
/**
 * ������������� �������� ��� ���������, ������� "���� ������" � "���� ���������" ���� ��������.
 *
 * ����������� ��� ���������� ���������� - ��������� �������� - (DWL_LOAD_FROM, DWL_LOAD_TILL),
 * �� ��������� ��� ������������ ��������� �������� LOAD_FROM � LOAD_TILL, ������� ������������ �
 * mvLoadFromVar, mvLoadTillVar, ���� ��� �������, ���� ������� � DWL_LOAD_FROM, DWL_LOAD_TILL.
 *
 * ������ �����, ��������� DWL_LOAD_ID ��������������� ��������.
 *
 * ���� ������� mvLoadFromVar/mvLoadTillVar, ��� ������ ���� ���������� ��� %global
 * ��� � ���������� �������.
 *
 * mvType ���������� ��� ��������.
 *  INCREMENTAL - ��������������� ��������, ����� ������ ��������� �������� ����������
 *                � LOAD_FROM = ��������� �������� LOAD_TILL+1. � ���� ������ ��������������
 *                ����������� �������� LAST_SUCCESSFUL_LOAD ��� ��������� DWL_LOAD_FROM.
 *  FULL - ������ ��������� �������� �� ������� �� ����������. � ���� ������ ��������
 *         DWL_LOAD_FROM �� ������������ (�� ������ ���� �����) � ��� �������� LOAD_FROM
 *         ��������������� ������ LOAD_TILL.
 *
 * ������������ LOAD_FROM �������� SAS date value, ����������� �� ��������� DWL_LOAD_FROM.
 *  ���� DWL_LOAD_FROM=LAST_SUCCESSFUL_LOAD (������ ��� mvType=INCREMENTAL), �� ����
 *    �������� "from" ����������� ��� ���� "till" ��������� �������� �������� �� ������
 *    ������-������� ���� 1 ����.
 *  ����� - ��������� ������� DWL_LOAD_FROM �� ������� DD/MM/YYYY.
 *
 * ������������ LOAD_TILL �������� SAS date value, ����������� �� ��������� DWL_LOAD_TILL.
 *  ���� DWL_LOAD_TILL=YESTERDAY, �� ��������� �����.
 *  ����� - ��������� ������� DWL_LOAD_TILL �� ������� DD/MM/YYYY.
 *
 * ��� ���������� ������ ���������������� LAST_SUCCESSFUL_LOAD ����� �� ��������
 * �������� mMarkSuccessfulLoad � �������� ����� ��������� ���������� ��������.
 */
%macro mGetLoadParams(mvBA, mvType, mvLoadFromVar=DWL_LOAD_FROM, mvLoadTillVar=DWL_LOAD_TILL);
	%DWL_INIT;
 
	%global DWL_LOAD_ID;
	%if ("&DWL_LOAD_ID" = "MAX") or ("&DWL_LOAD_ID" = "") %then %do;
		%DWL_LOAD_ID_INIT; /* �������� ������������� �������� -> DWL_LOAD_ID.*/
		%if %DWL_NOT_OK %then %goto EXIT;
	%end; %else %if %sysfunc(exist(&DWL_REGLOADS_LOG)) %then %do;
		/* �� �������� �� ��� ���-�� ������ ��� ����� ������� � ����� ��������? */
		%local mvLoadId;
		proc sql noprint;
			select max(load_id) into :mvLoadId
				from &DWL_REGLOADS_LOG where load_id = &DWL_LOAD_ID;
		quit;
		%if %DWL_NOT_OK %then %goto EXIT;
 
		%if &mvLoadId = &DWL_LOAD_ID %then %do;
			%DWL_RAISE_ERROR("Load with ID=&DWL_LOAD_ID and BA=&mvBA is already logged.");
			%DWL_RAISE_ERROR("(Did you accidentally call mGetLoadParams twice?)");
			%goto EXIT;
		%end;
	%end;
 
	%local DWL_LOAD_FROM_NOXST;
    %mSymExist(DWL_LOAD_FROM, DWL_LOAD_FROM_NOXST);
    %if &DWL_LOAD_FROM_NOXST %then %let DWL_LOAD_FROM=;
 
	%if "&mvType" ^= "FULL" and "&mvType" ^= "INCREMENTAL" %then %do;
		%DWL_RAISE_ERROR("Unsupported mvType: &mvType. Must be FULL or INCREMENTAL."); %goto EXIT;
	%end; %else %if "&mvType" = "FULL" and "&DWL_LOAD_FROM" ^= "" %then %do;
		%DWL_RAISE_ERROR("DWL_LOAD_FROM must only be set for INCREMENTAL loads."); %goto EXIT;
	%end;
 
	%put NOTE: parameters DWL_LOAD_FROM=<&DWL_LOAD_FROM>, DWL_LOAD_TILL=<&DWL_LOAD_TILL>;
 
	/* ������������ ����������� �������� DWL_LOAD_FROM/DWL_LOAD_TILL ���
	 * ��������� ���� � ������� DD/MM/YYYY. */
 
    %if &DWL_LOAD_TILL = YESTERDAY %then %do; /* ����������� �������� ��� ������������ �������� - ���������� �����. */
		%let &mvLoadTillVar = %sysfunc(intnx(day, "&SYSDATE9"d, -1));
    %end; %else %do; /* ��������� �� ������� DD/MM/YYYY. */
		%let &mvLoadTillVar = %sysfunc(inputn(&DWL_LOAD_TILL, DDMMYY10.));
    %end;
 
	%if "&mvType" = "FULL" %then %do;
		%let &mvLoadFromVar = &&&mvLoadTillVar;
	%end; %else %if &DWL_LOAD_FROM = LAST_SUCCESSFUL_LOAD %then %do;
		%let &mvLoadFromVar = .;
 
		%if %sysfunc(exist(&DWL_REGLOADS_LOG)) %then %do;
			%local mvLastSuccessfulLoadID;
			proc sql noprint;
				select max(load_id) format 18. into :mvLastSuccessfulLoadID
					from &DWL_REGLOADS_LOG
					where ba = "&mvBA" and successful = 1;
			quit;
			%if %DWL_NOT_OK %then %goto EXIT;
 
			proc sql noprint;
				select max(load_till)+1 format 18. into :&mvLoadFromVar
					from &DWL_REGLOADS_LOG
					where ba = "&mvBA" and successful = 1 and load_id = &mvLastSuccessfulLoadID;
				
			quit;
			%if %DWL_NOT_OK %then %goto EXIT;
		%end;
 
		%if &&&mvLoadFromVar = . %then %do;
			%DWL_RAISE_ERROR ("DWL_LOAD_FROM is set to LAST_SUCCESSFUL_LOAD, but this looks like a first run");
			%DWL_RAISE_ERROR ("(no successful loads for ba=<&mvBa> in &DWL_REGLOADS_LOG).");
			%DWL_RAISE_ERROR ("You must set DWL_LOAD_FROM to a specific date in the DD/MM/YYYY format.");
			%goto EXIT;
		%end;
	%end; %else %do;/* ��������� �� ������� DD/MM/YYYY. */
		%let &mvLoadFromVar = %sysfunc(inputn(&DWL_LOAD_FROM, DDMMYY10.));
	%end;
 
	/* ��������� ������������ ����������� ����������. */
	%if &&&mvLoadTillVar = . %then %do;
		%DWL_RAISE_ERROR("DWL_LOAD_TILL has invalid value.");
		%DWL_RAISE_ERROR("DWL_LOAD_TILL must be set to a specific date (DD/MM/YYYY)");
		%DWL_RAISE_ERROR("or to a special value YESTERDAY.");
		%goto EXIT;
    %end;
	%if &&&mvLoadFromVar = . %then %do;
		%DWL_RAISE_ERROR("DWL_LOAD_FROM has invalid value.");
		%DWL_RAISE_ERROR("DWL_LOAD_FROM must be set to a specific date (DD/MM/YYYY)");
		%DWL_RAISE_ERROR("or to a special value LAST_SUCCESSFUL_LOAD.");
		%goto EXIT;
    %end;
	%if &DWL_LOAD_FROM > &DWL_LOAD_TILL %then %do;
		%DWL_RAISE_ERROR("DWL_LOAD_FROM > DWL_LOAD_TILL!");
		%DWL_RAISE_ERROR("Did you run the process twice with DWL_LOAD_FROM=LAST_SUCCESSFUL_LOAD today?");
		%goto EXIT;
	%end;
 
    %if not %sysfunc(exist(&DWL_REGLOADS_LOG)) %then %do;
		data &DWL_REGLOADS_LOG;
			attrib
				load_id 	length=4	label="������������� ��������"
				ba			length=$8	label="������������� ���������� �������"
				load_from	length=6	label="���� ������ ���� ��������"		format=DATE.
				load_till	length=6	label="���� ��������� ���� ��������"	format=DATE.
				load_start_dttm length=6 label="����-����� ������ ��������"		format=DATETIME.
				load_end_dttm 	length=6 label="����-����� ��������� ��������"		format=DATETIME.
				successful	length=3	label="������� ��������� ����������"
				;
			delete;
        run;
		%if %DWL_NOT_OK %then %goto EXIT;
    %end;
 
    /* ��������� ������ � ������ �������� � DWL_REGLOADS_LOG. */
	proc sql noprint;
		insert into &DWL_REGLOADS_LOG
			set load_id=&DWL_LOAD_ID,
				ba="&mvBA",
				load_from=&DWL_LOAD_FROM,
				load_till=&DWL_LOAD_TILL,
				load_start_dttm=&DWL_LOAD_START_DTTM,
				load_end_dttm=.,
				successful=.;
	quit;
	%if %DWL_NOT_OK %then %goto EXIT;
 
%EXIT:
	%DWL_TERM;
%mend mGetLoadParams;
 
/**
 * �������� �������� ������ ���������� �������, ������� ������� mGetLoadParams,
 * ��� ��������. ���������� �������� ��� ���������� ������ LAST_SUCCESSFUL_LOAD.
 */
%macro mMarkSuccessfulLoad(mvBA);
	%if not %DWL_NOT_OK %then %do;
		proc sql;
			update &DWL_REGLOADS_LOG
				set successful=1, load_end_dttm=datetime()
				where load_id = &DWL_LOAD_ID;
		quit;
	%end;
%mend mMarkSuccessfulLoad;
 
%macro mTest_RegLoadInitIncr;
	%include "&SVNROOT\common\ErrorControl.sas";
	%include "&SVNROOT\common\LoadInitialization.sas";
	%let DWL_PROCESS_NAME=test; %let DWL_NOCHECKLOG=1;
	%DWL_START_LOADING;
 
	%macro mTest(mvType, mvFrom, mvTill, mvExpectedFrom, mvExpectedTill);
		%let DWL_LOAD_FROM = &mvFrom;
		%let DWL_LOAD_TILL = &mvTill;
		%mGetLoadParams(TEST, &mvType);
		%if %DWL_NOT_OK %then %goto EXIT;
 
		%if &DWL_LOAD_FROM ^= %sysfunc(inputn(&mvExpectedFrom, DDMMYY10.)) %then %do;
			%DWL_RAISE_ERROR("From param is not as expected: &DWL_LOAD_FROM vs &mvExpectedFrom"); %goto EXIT;
		%end;
		%if &DWL_LOAD_TILL ^= %sysfunc(inputn(&mvExpectedTill, DDMMYY10.)) %then %do;
			%DWL_RAISE_ERROR("Till param is not as expected: &DWL_LOAD_TILL vs &mvExpectedTill");  %goto EXIT;
		%end;
	%EXIT:
	%mend mTest;
 
	%if %sysfunc(exist(&DWL_REGLOADS_LOG)) %then %do;
		data &DWL_REGLOADS_LOG;
			set &DWL_REGLOADS_LOG;
			if ba ^= "TEST";
		run;
		%if %DWL_NOT_OK %then %goto EXIT;
	%end;
 
	%symdel DWL_LOAD_ID;
	%mTest(INCREMENTAL, 01/01/2008, 02/01/2008, 01/01/2008, 02/01/2008);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%symdel DWL_LOAD_ID;
	%mTest(INCREMENTAL, 01/01/2008, 02/01/2008, 01/01/2008, 02/01/2008);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mMarkSuccessfulLoad(TEST);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%symdel DWL_LOAD_ID;
	%mTest(INCREMENTAL, LAST_SUCCESSFUL_LOAD, 03/01/2008, 03/01/2008, 03/01/2008);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%symdel DWL_LOAD_ID;
	%mTest(FULL, , 03/01/2008, 03/01/2008, 03/01/2008);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%put NOTE: All tests passed &DWL_LOAD_ID;
 
%EXIT:
%mend mTest_RegLoadInitIncr;
 
 
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\RegLoadInitialization.sas ****/
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\DWL_UNX_RENAME.sas ****/
%MACRO mFileMove(mvFileFrom, mvFileTo);
 
  /* Check for path equality */
  %IF %QUOTE(&mvFileFrom) = %QUOTE(&mvFileTo) %THEN %DO;
    %PUT ERROR: Could not move file to itself.;
    %GOTO ERREXIT;
  %END;
 
  %IF %SYSFUNC(FileExist(&mvFileTo)) %THEN %DO;
    SYSTASK COMMAND "/usr/bin/rm -f &mvFileTo" WAIT;
 
    %IF %SYSFUNC(FileExist(&mvFileTo)) %THEN %DO;
      %PUT ERROR: File &mvFileTo cannot be deleted. Move aborted.;
      %GOTO ERREXIT;
    %END;
  %END;
 
  SYSTASK COMMAND "/usr/bin/mv &mvFileFrom &mvFileTo" WAIT;
 
  %IF NOT %SYSFUNC(FileExist(&mvFileTo)) %THEN %DO;
     %PUT ERROR: Cannot rename &mvFileFrom to &mvFileTo.;
     %GOTO ERREXIT;
  %END; %ELSE %DO;
    %PUT NOTE: Moving &mvFileFrom to &mvFileTo.;
  %END;
 
  %GOTO EXIT;
 
%ERREXIT:
  %LET SYSRC=29;
%EXIT:
%MEND mFileMove;
 
/**
 * ������ ����������� ����������� ������ � UNIX.
 *  mvFrom - �������, ������� �������� (���� <libname>.<memname>,
 *           ���� <libname> ������, ������������ WORK)
 *  mvTo   - �������, ���� �������� (��� �� ������)
 *  mvType - ���� ���������� ������� - MDDB, �� ���� ������ MDDB,
 *           ����� - ����� ���������� ��������� ��������.
 *
 * ������ ������������ ��� ����������� ��������� ������ � UNIX.
 * ��������, ���� �� ��������� �������� ������� MTS_DETL.data, �
 * ��� � ��� ����� ������������ ��������. ���� �� ��������� �������
 * ������� `MTS_DETL.data_temp`, � ����� ��������� ������
 * DWL_UNX_RENAME (MTS_DETL.data_temp, MTS_DETL.data),������ ���������
 * ������������ ������ �������, � ��� ����� ��������� ����� ��� � �����
 * ������� (��� ����������, ���� ���������� UNIX ������� ����� �������,
 * � ����� ����������� ����� ������ ���). � ������, ����������� �������,
 * ��� ���� �� ������.
 *
 * ������ ������������� ���������� ����� ����� ��������, ���� ��� ���� � �������.
 */
 
%MACRO DWL_UNX_RENAME (mvFrom, mvTo, mvType);
  %LOCAL mvLibFrom mvMemFrom mvPathFrom mvFileFrom mvLibTo mvMemTo mvPathTo
mvFileTo;
 
  %IF %LENGTH(&mvType)=0 %THEN %LET mvType=DATA;
 
 /* %IF NOT (%QUOTE(%SYSFUNC(Upcase(&SYSSCPL))) = %QUOTE(HP-UX) OR
%QUOTE(%SYSFUNC(Upcase(&SYSSCPL))) = SUNOS) %THEN %DO;
    %PUT ERROR: Sorry, for SunOS and HP-UX only.;
    %GOTO ERREXIT;
  %END;*/
 
  %IF NOT (&mvType=MDDB OR &mvType=DATA) %THEN %DO;
    %PUT ERROR: Memtype &mvType. not supported.;
    %GOTO ERREXIT;
  %END;
 
  /* Extract libnames and memnames */
  %IF %INDEX(&mvFrom, .)>0 %THEN %DO;
    %LET mvLibFrom = %SCAN(&mvFrom,1,.);
    %LET mvMemFrom = %SCAN(&mvFrom,2,.);
  %END; %ELSE %DO;
    %LET mvLibFrom = WORK;
    %LET mvMemFrom = &mvFrom;
  %END;
 
  %IF %INDEX(&mvTo, .)>0 %THEN %DO;
    %LET mvLibTo = %SCAN(&mvTo,1,.);
    %LET mvMemTo = %SCAN(&mvTo,2,.);
  %END; %ELSE %DO;
    %LET mvLibTo = WORK;
    %LET mvMemTo = &mvTo;
  %END;
 
  /* Physical paths for libraries */
  %LET mvPathFrom = %SCAN(%SYSFUNC(Pathname(&mvLibFrom)), 1, " ()'");
  %IF %LENGTH(&mvPathFrom)=0 %THEN %DO;
    %PUT ERROR: Libname &mvLibFrom is not assigned.;
    %GOTO ERREXIT;
  %END;
 
  %LET mvPathTo = %SCAN(%SYSFUNC(Pathname(&mvLibTo)), 1, " ()'");
  %IF %LENGTH(&mvPathTo)=0 %THEN %DO;
    %PUT ERROR: Libname &mvLibTo is not assigned.;
    %GOTO ERREXIT;
  %END;
 
  %IF NOT %SYSFUNC(Exist(&mvLibFrom..&mvMemFrom,&mvType)) %THEN %DO;
    %PUT ERROR: File &mvLibFrom..&mvMemFrom..&mvType does not exist.;
    %GOTO ERREXIT;
  %END;
 
  %LET mvMemFrom = %SYSFUNC(Lowcase(&mvMemFrom));
  %LET mvMemTo   = %SYSFUNC(Lowcase(&mvMemTo));
 
  %IF &mvType=DATA %THEN %DO;
    /* Move data set */
    %LET mvFileFrom =&mvPathFrom./&mvMemFrom..sas7bdat;
    %LET mvFileTo   =&mvPathTo./&mvMemTo..sas7bdat;
    %mFileMove(&mvFileFrom, &mvFileTo);
    %IF &SYSRC>0 %THEN %GOTO EXIT;
 
    /* Move indexes if exist */
    %LET mvFileFrom =&mvPathFrom./&mvMemFrom..sas7bndx;
    %LET mvFileTo   =&mvPathTo./&mvMemTo..sas7bndx;
    %IF (%SYSFUNC(FileExist(&mvFileFrom))) %THEN %DO;
       %mFileMove(&mvFileFrom, &mvFileTo);
       %IF &SYSRC>0 %THEN %GOTO EXIT;
    %END;
  %END; %ELSE %DO;
    /* Move MDDB */
    %LET mvFileFrom =&mvPathFrom./&mvMemFrom..sas7bmdb;
    %LET mvFileTo   =&mvPathTo./&mvMemTo..sas7bmdb;
    %mFileMove(&mvFileFrom, &mvFileTo);
    %IF &SYSRC>0 %THEN %GOTO EXIT;
  %END;
 
  %GOTO EXIT;
 
%ERREXIT:
  %LET SYSRC=29;
%EXIT:
%MEND DWL_UNX_RENAME;
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\DWL_UNX_RENAME.sas ****/
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\mDiffExtractor.sas ****/
/**
 * ���������� ������� mvTableA c �������� mvTableB � ������� ������� � �����������
 * � B �� ��������� � A - mvOutDiff.
 *
 * ������� mvTableA � mvTableB ������ ����� ���������� ��������� � ����� �����, �������
 * ���� � mvTableB (� ���������, mvKeyList � mvIgnoreList). ������� mvTableA ������
 * ������������� ����� ���� valid_from.
 *
 * ������� mvTableA � mvTableB ������ ���� ������������� �� mvKeyList � ����� �� �����
 * ����� ������ ��� ������ ���������� �������� ����� mvKeyList (�.�. ���� mvKeyList
 * �������� ���������� ������ ������ �� ������).
 *
 * ��������� ���� �� ����� mvKeyList. ��� ������ ���� ��������������� ������� �
 * mvTableA � mvTableB ������������ (���������� "^=") �������� ��������� �����,
 * ����� ������������� � mvIgnoreList.
 *
 * �������� ������� ����� ��� ���� ������� B, ���� valid_from, valid_to.
 * ��� ����� ������������� �� mvKeyList � �������� ����� ������, ����� � ����������
 *   merge mvTableA mvOutDiff;
 *   by &mvKeyList valid_from;
 *   if valid_to = &mvInf;
 *   drop valid_from valid_to;
 * - ���������� ������� mvTableB (� ���������� ��������� � mvIgnoreList).
 *
 * ���������:
 *  mvOutDiff, mvTableA, mvTableB - �������� ������ � ������� libname.memname ���
 *                                  ������ memname (��� ������ � work)
 *  mvUpdatedTable - ���� �������, � ��� ������� ������������ ����� ���������� �� valid
 *                   ����� ������.
 *  mvKeyList, mvIgnoreList - ������ ����� ����� ������.
 *  mvIgnoreList ����� ���� ������, ���� ��������� ������ ������ ���� �� ���� �����.
 *  mvNow, mvInf - �������� SAS datetime, ������������ ������ ��������� � ������
 *                 "�������� �������������" ��� ������������� � ����� valid_from �
 *                 valid_to � mvOutDiff.
 */
%macro mDiffExtractor(mvOutDiff, mvTableA, mvTableB, mvKeyList, mvIgnoreList=,
			 		  mvNow=%sysfunc(datetime()), mvInf='01JAN2040:00:00:00'dt,
					  mvUpdatedTable=);
	%local mvTableB_LibName mvTableB_MemName ;
	%mExtractLibNameMemName(&mvTableB, mvTableB_LibName, mvTableB_MemName);
    %if %DWL_NOT_OK %then %goto EXIT;
 
    /*��������� ������ � ��������� �������� �� ���� a b c  �  'a','b','c'*/
	%local mvKey mvIgnore;
    data _null_;
         call symput( 'mvKey', "'" || tranwrd (trim("&mvKeyList"), " ", "','") || "'");
         call symput( 'mvIgnore', "'" || tranwrd (trim("&mvIgnoreList"), " ", "','") || "'");
    run;
    %if %DWL_NOT_OK %then %goto EXIT;
 
    /*�������� ����� �������� ��� ������ �������*/
	%local mvKeepList mvRenameList mvRenameBackList mvCompareList ;
    proc sql noprint;
        create table columnTable as
	        select name,
	               upcase(name) in ( %upcase(&mvKey) ) as keyFlag,
	               upcase(name) in ( %upcase(&mvIgnore) ) as Ignore
	         from dictionary.columns
	        where libname="%upcase(&mvTableB_LibName)" and memname="%upcase(&mvTableB_MemName)";
 
        select  name,
                trim(left(name))||"=__"||trim(left(name)),
                trim(left(name))||"=__"||trim(left(name))
                into
                    :mvKeepList separated by ' ',/*��� ���� ����� ��������*/
                    :mvRenameList separated by ' ',/*�������������� ���� __���=���*/
                    :mvRenameBackList separated by ';'/*������������ ���� ���=__���; */
	        from columnTable
	        where keyFlag=0;
 
        select trim(left(name))||"^=__"||trim(left(name))
                into
                    :mvCompareList separated by ' or '
	        from columnTable
	        where keyFlag=0 and Ignore=0;
 
		drop table columnTable;
    quit;
    %if %DWL_NOT_OK %then %goto EXIT;
 
    /*������� ����� ���������� - ������ ��� ��������*/
    %put mvKeyList      - &mvKeyList;
    %put mvKeepList     - &mvKeepList;
    %put mvRenameList   - &mvRenameList;
    %put mvCompareList  - &mvCompareList;
 
	%local mvOutputUpdated; %let mvOutputUpdated=;
    data &mvOutDiff (keep = &mvKeyList &mvKeepList valid_from valid_to)
		%if "&mvUpdatedTable" ^= "" %then %do;
		 &mvUpdatedTable (keep = &mvKeyList &mvKeepList valid_from)
		 %let mvOutputUpdated = output &mvUpdatedTable;
		%end;
		;
        attrib
            valid_from      format=datetime.        length=6
            valid_to        format=datetime.        length=6
			;
        merge   &mvTableA (in=in_old keep=&mvKeyList &mvKeepList valid_from) /*����������� ������*/
                &mvTableB (in=in_new keep=&mvKeyList &mvKeepList
									 rename=(&mvRenameList)); /*������ ������*/
        by &mvKeyList;
 
		%local mvLastKeyVar; /* ��������� ���� � mvKeyList */
    	%let mvLastKeyVar = %scan(&mvKeyList, -1, %str( ));
        if last.&mvLastKeyVar ; /* ������� ������ �� ��������� ������ ��� ������� �������� "�����" �������. */
 
        if in_new and not in_old then do; /*� �������� ���� ��������� ������*/
            /* �.� ������ �����, ����������� �� Valid */
            &mvRenameBackList ;
            valid_from=&mvNow;
            valid_to=&mvInf;
            output &mvOutDiff;
			&mvOutputUpdated;
        end; else if not in_new and in_old then do; /*� ��������� ������� ������*/
            /*������ ���� �������,������������� ��������� valid_to � ������ ������ "�� ���������"*/
            valid_to=&mvNow;
            output &mvOutDiff;
        end; else if in_new and in_old then do; /*�������� ������ ����������*/
            if &mvCompareList then do;
                /*������� ������ ������*/
                valid_to=&mvNow;
                output &mvOutDiff;
 
                /*������� ������ ������*/
                &mvRenameBackList ;
 
                valid_from=&mvNow;
                valid_to=&mvInf;
                output &mvOutDiff;
            end;
			&mvOutputUpdated;
        end;
    run;
	%if %DWL_NOT_OK %then %goto EXIT;
%EXIT:
%mend mDiffExtractor;
 
/**
 * ���� mvValidHistoryTable �� ����������, ������� �� (������) ��
 * ����������, ��� � mvTable, � ��������������� ������ valid_from,
 * valid_to � is_valid ���� mvCreateIsValid=1. */
%macro mMakeSureValidHistoryTableExists(mvValidHistoryTable, mvTable, mvCreateIsValid=0);
    %if not %sysfunc(exist(&mvValidHistoryTable, DATA)) %then %do;
        %put NOTE: &mvValidHistoryTable does not exist. New table will created.;
 
        data &mvValidHistoryTable;
            attrib
                valid_from      format=datetime.        length=6
                valid_to        format=datetime.        length=6
			%if &mvCreateIsValid %then %do;
                is_valid        format=1.               length=3    label='������������'
			%end;
			;
            set &mvTable (obs=0);
            valid_from = .;  /* �� ���������� call missing, ����� �������� � ������� �� SASv8 */
            valid_to = .;
			%if &mvCreateIsValid %then %do;
	            is_valid = .;
			%end;
        run;
        %if %DWL_NOT_OK %then %goto EXIT;
    %end;
%EXIT:
%mend mMakeSureValidHistoryTableExists;
 
/**
 * �� ����� ������� � ������� lib.memname ��� memname (mvTableName)
 * ��������� ����������, ��������� � mvLibVar � mvMemVar �����������
 * � memname �������. */
%macro mExtractLibNameMemName(mvTableName, mvLibVar, mvMemVar);
	%if %index(&mvTableName, .)>0 %then %do;
		%let &mvLibVar = %scan(&mvTableName,1,.);
		%let &mvMemVar = %scan(&mvTableName,2,.);
	%end; %else %do;
		%let &mvLibVar = WORK;
		%let &mvMemVar = &mvTableName;
	%end;
%mend mExtractLibNameMemName;
 
 
%macro mTest_DiffExtractor;
	option mprint mlogic symbolgen;
	%macro mTest_Compare( mvTable1, mvTable2 );
	    PROC COMPARE BASE= &mvTable1 COMPARE=&mvTable2 method=relative ERROR NOSUMMARY;
	    RUN;
	%mend mTest_Compare;
 
	proc sql;
		drop table work.table_a;
	quit;
	%if %DWL_NOT_OK %then %goto EXIT;
 
	/* ���� 1. diff ������ ������� � �������� ��������� �� ������ ������� � ��������. */
	data work.table_b ;
		retain sas_key .;
		Key1 = 1; Key2 = 1; Value = 0; output;
		Key1 = 1; Key2 = 2; Value = 2; output;
		Key1 = 2; Key2 = 3; Value = 4; output;
	run;
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mMakeSureValidHistoryTableExists(
		mvValidHistoryTable=table_a,
		mvTable=table_b);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mDiffExtractor(
		mvOutDiff=diff,
		mvTableA=table_a,
		mvTableB=table_b,
		mvKeyList=Key1 key2, mvNow = "01MAY2008:00:00:00"dt);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	data diff_etalon (drop=is_valid);
        attrib
            valid_from      format=datetime.        length=6
            valid_to        format=datetime.        length=6
			;
		valid_from = "01MAY2008:00:00:00"dt;
		valid_to = "01JAN2040:00:00:00"dt;
		set work.table_b ;
	run;
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mTest_Compare(work.diff, diff_etalon);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	/* ���� 2. diff �������� ������� � ����������� (��������, ���������, ���������� �������) */
 
	data t;
		a=1;b=1;sas_key = 2; is_valid = 1; Key1 = 1; Key2 = 1; Value = 0; output;
		a=1;b=0;sas_key = 3; is_valid = 0; Key1 = 1; Key2 = 2; Value = 2; output;
		a=0;b=1;sas_key = 5; is_valid = 1; Key1 = 1; Key2 = 2; Value = 3; output;
		a=0;b=1;sas_key = 6; is_valid = 1; Key1 = 1; Key2 = 3; Value = 6; output;
		a=1;b=0;sas_key = 4; is_valid = 0; Key1 = 2; Key2 = 3; Value = 4; output;
	run;
	%if %DWL_NOT_OK %then %goto EXIT;
 
	data work.full_history diff_etalon (drop=a b is_valid);
        attrib
            valid_from      format=datetime.        length=6
            valid_to        format=datetime.        length=6
			;
		set t;
		sas_key = .;
		if a and b then do;
			valid_from = "01MAY2008:00:00:00"dt;
			valid_to = "01JAN2040:00:00:00"dt;
			output full_history;
		end; else if a and not b then do;
			valid_from = "01MAY2008:00:00:00"dt;
			valid_to = "02MAY2008:00:00:00"dt;
			output full_history; output diff_etalon;
		end; else do; /* b and not a*/
			valid_from = "02MAY2008:00:00:00"dt;
			valid_to = "01JAN2040:00:00:00"dt;
			output full_history; output diff_etalon;
		end;
	run;
	%if %DWL_NOT_OK %then %goto EXIT;
 
	data table_a (drop=a b valid_to is_valid)
		 table_b (drop = a b is_valid valid_from valid_to)
		 new_etalon (drop = a b valid_to is_valid);
		set work.full_history;
		sas_key = .;
		if b then do;
			output table_b;
			output new_etalon;
		end;
		if a then do;
			valid_to = "01JAN2040:00:00:00"dt;
			output table_a;
		end;
	run;
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mDiffExtractor(
		mvOutDiff=diff,
		mvTableA=table_a,
		mvTableB=table_b,
		mvKeyList=Key1 key2, mvIgnoreList=sas_key, mvNow = "02MAY2008:00:00:00"dt);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mTest_Compare(diff, diff_etalon);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	/* ���� 3. �� ��, ��� � 2, �� � ������� ����������� �������. */
 
	%mDiffExtractor(
		mvOutDiff=diff,
		mvTableA=table_a,
		mvTableB=table_b,
		mvKeyList=Key1 key2, mvIgnoreList=sas_key, mvNow = "02MAY2008:00:00:00"dt,
		mvUpdatedTable = new);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mTest_Compare(diff, diff_etalon);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mTest_Compare(new, new_etalon);
	%if %DWL_NOT_OK %then %goto EXIT;
%EXIT:
%mend mTest_DiffExtractor;
 
 
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\common\mDiffExtractor.sas ****/
 /**** INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\dwh\region\common\mCreateTransportArchive.sas ****/
/*
 *  Date:   22.12.2004
 *  Author: ������� ��������
 *  Desc:   ������ ��� �������� ������������� ������
 *  Params:
 *          mvEntry - �������, ������� ����� ��������� � ������������ ����� (� ������� LibName.EntryName)
 *          mvBusinessArea - ��������� ��� ������-������� (������ �� ��� ������������� ������)
 *          mvFromDate,mvToDate,mvMiddleDate - ����, ������������ �������� �������� � ������� numeric
 */
%macro mCreateTransportArchive(mvEntry, mvBusinessArea, mvFromDate, mvToDate, mvMiddleDate);
 
    %DWL_INIT;
	%if %DWL_NOT_OK %then %goto EXIT;
 
    *   ��������� ������� � �������� ����� ������ ;
 
    %LOCAL mvFromDateStr mvToDateStr;
 
    %let mvLibName = %scan(&mvEntry, -2, .);
    %let mvElementName = %scan(&mvEntry, -1, .);
 
    *   ������ ���������� - ��� Work;
    %if &mvLibName = %str() %then %let mvLibName = Work;
 
    *   ������� - ������������� ����������;
    %IF &mvFromDate NE %str() %THEN
        %let mvFromDateStr = %lowcase( %sysfunc( putn(&mvFromDate, date7.) ) );
 
    %IF &mvToDate NE %str() %THEN
        %let mvToDateStr = %lowcase( %sysfunc( putn(&mvToDate, date7.) ) );
 
    %let mvTransportPrefix = %lowcase(&mvBusinessArea)_%sysfunc(Trim(&DWL_LOAD_ID));
    %let mvTransportPrefix = &mvTransportPrefix._&mvFromDateStr._&mvToDateStr;
 
    %if &mvMiddleDate ^= %str() %then
        %let mvMiddleDate = %lowcase( %sysfunc( putn(&mvMiddleDate, date7.) ) );
 
    %if &mvMiddleDate ^= %str() and &mvMiddleDate ^= . %then
    	%let mvTransportPrefix = &mvTransportPrefix._&mvMiddleDate;
 
    %let mvFileName = %lowcase(&mvElementName);
    %let mvFilePath = %sysfunc(pathname(&mvLibName))/&mvFileName..sas7bdat;
    %let mvArchivedFilePath = &REGDATA_PATH/&mvTransportPrefix..Z;
 
    *  ���������� �������� ����� ;
    data _null_;
       _error_ = system("compress -c &mvFilePath > &mvArchivedFilePath");
    run;
 
    %if %DWL_NOT_OK %then %goto EXIT;
 
%EXIT:
    %DWL_TERM;
 
%mend mCreateTransportArchive;
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\dwh\region\common\mCreateTransportArchive.sas ****/
 
/**
 * ����� ��� �������� ������ �� ������������ ��������� � ����������
 * ������������ ������, ���������� ��������� �� ��������� � ����������
 * �� ���������� ��������. ��������� �������� � ������� � ������:
 *     <���� ����������� �������>, valid_from, valid_to
 * ��������� � ������� ������� ��. mDiffExtractor.
 *
 * �����������, ��� �������, ��� ��������
 * ������� ������, ��� ������� ������ �������� ��������� ������ ���
 * ��������������� ��-�� �������� ������ ������������ ������.
 *
 * ���������:
 *  mvBA - ��� ���������� �������. ���������� �������� ����������, ��������� ������
 *         � ������ � ��������� ����� �������� (��. mGetLoadParams).
 *  mvKeyList - ����� �����, ������������ ���������� ���� ������ � �������.
 *              ������ ����� ����� � ���������� ������������ ���������� �������,
 *              ����������� �������� mvLoadDataFromOracle.
 *  mvHistoryLength - �� ������� ���� �� DWL_LOAD_FROM �������������� ���������
 *                    "������ ������" � ���������.
 *  mvLoadActualData - �������� �������, ��������������� �������� ���������� ������
 *                     ������ ����� ��������� ���������:
 *      mvNewLoadTable  - �������� �������, � ������� ���������� ��������� ���������� ������.
 *                        ��������� ������� ������ ���� ������������� �� mvKeyList � �� ��������� ����������.
 *      DWL_FIRST_LOAD  - ���� 1, �� ������ �������� (��������� ������� �������).
 *      mvHistoryDateOra - �� ��������� ������, ������� ����������� ����� mvHistoryDateOra.
 *  mvTrimLastLoad - �������� �������, ��������������� ������� ������ ������� �������� ��
 *                   "������" �������, �� ������������� � ���� ��� �� Oracle. ������ �����
 *                   ��������� ���������:
 *      mvOutView - ����������� view
 *      mvLastLoadTable - ������ ��������� �������� ��� �������.
 *      mvHistoryDate - ���� ������ ���� �������� (�� ��, ��� ���������� � mvLoadActualData).
 *
 *  ���� ����������� ������ ��� effective-������������, �� �������� mvHistoryLength ���� ��������.
 *  � ���� ������ �������� mvTrimLastLoad ����� �� ������������.
 *  ����� ����, � ���� ������ ����� ���������� ���������� ������ ������� mvLoadActualData, � �������
 *  ���� ������ �������� mvNewLoadTable.
 */
%macro mCreateDiffTransport(mvBA, mvKeyList, mvHistoryLength, mvLoadActualData, mvTrimLastLoad);
	%local mvLastLoadTable mvNewLoadTable;
	/* �������, � ������� �������� ���� ������ �� Oracle �� ��������� �������� ��������, � �������
	 * ���������� ���������. � ��� ������ ���� ������� mvHistoryLength ���� �������.
	 */
	%let mvLastLoadTable = MTS_DETL.LAST_&mvBA;
	/* �������, � ������� ���������� �������� ����������� ����� ������ �� Oracle.
	 */
	%let mvNewLoadTable = WORK.&mvBA;
 
	/* ��������� FROM � TILL �� ���������������, ������ ��� ��� �� ����� �������
	 * ������ ��� �������� diff-���, ��� � ���� ��������. ������� ��������� �������
	 * ������ �� ��������� N ����, � �������� ������ ��������� �� ��������� � �������
	 * �� ������ ���������� ��������.
	 */
	%local DWL_LOAD_FROM DWL_LOAD_TILL;
	%let DWL_LOAD_TILL = YESTERDAY;
	%if "&DWL_FIRST_LOAD" = "1" %then %do;
		%let DWL_LOAD_FROM = 01/01/1990;
	%end; %else %do;
		%let DWL_LOAD_FROM = LAST_SUCCESSFUL_LOAD;	
	%end;
 
	/* ������������ YESTERDAY/LAST_SUCCESSFUL_LOAD � DWL_LOAD_FROM, DWL_LOAD_TILL
	 */
	%mGetLoadParams(&mvBA, INCREMENTAL);
    %if %DWL_NOT_OK %then %goto EXIT;
	
	%if ("&DWL_FIRST_LOAD" ^= "1") and not %sysfunc(exist(&mvLastLoadTable)) %then %do;
		%DWL_RAISE_ERROR("&mvLastLoadTable does not exist. You must run the ");
		%DWL_RAISE_ERROR("first load: DWL_FIRST_LOAD=1.");
		%if %DWL_NOT_OK %then %goto EXIT;
	%end;
 
	%if("&mvHistoryLength" ^= "" ) %then %do;
		/* ��� �������� �����, ���� ��� �� ������ ��������, ������ � ������� ������ �� ����������
		 * ��� �������� �� ����� ��� mvHistoryLength ���� ����� �������.
		 * �������������, �� Oracle ���������, � � mvLastLoadTable ������, ������ ��� ������.
		 */
		%local mvHistoryDateOra mvHistoryDate; /* ���� "���������" ������ ������ � ������� Oracle � SAS. */
		data _null_;
			history_date = intnx('day', &DWL_LOAD_FROM, -&mvHistoryLength);
			call symput('mvHistoryDateOra', "'" || put(history_date , date9.) || " 00:00:00'");
			call symput('mvHistoryDate', dhms(history_date, 0 , 0 , 0));
		run;
		%if %DWL_NOT_OK %then %goto EXIT;
		
		/* ���������� ���������� ������ �� ��������� mvHistoryLength ���� �� Oracl� � mvNewLoadTable. */
		%&mvLoadActualData(&mvNewLoadTable, &DWL_FIRST_LOAD, &mvHistoryDateOra);
	%end;
	%else %do;
		%&mvLoadActualData(&mvNewLoadTable);
	%end;
	%if %DWL_NOT_OK %then %goto EXIT;
 
 
	%if "&DWL_FIRST_LOAD" = "1" %then %do;
		proc sql; drop table &mvLastLoadTable; quit;
	    %if %DWL_NOT_OK %then %goto EXIT;
 
		/* ������� mvLastLoadTable ����� �� ���������, ��� ����������� �� Oracle �������
		 * ���� valid_from, valid_to, is_valid. */
		%mMakeSureValidHistoryTableExists(&mvLastLoadTable, &mvNewLoadTable);
		%if %DWL_NOT_OK %then %goto EXIT;
	%end;
 
	%local mvLastLoadTrimmed;
	%let mvLastLoadTrimmed = &mvLastLoadTable;
 
	/* ������� ������ ������, ������� �� ����������� �� Oracle.
	 * (������ ��� �������� � �������� ������ effective-������)
	 */
	%if("&mvHistoryLength" ^= "" ) %then %do;
		%let mvLastLoadTrimmed = last_load;
		%&mvTrimLastLoad (mvOutView = &mvLastLoadTrimmed,
					      mvLastLoadTable = &mvLastLoadTable,
					      mvHistoryDate = &mvHistoryDate
						  );
   		%if %DWL_NOT_OK %then %goto EXIT;
	%end;
	
	/* ��������� ��������� � ����������� �� Oracle �������� �� ��������� �
	 * ����������� ������� �������� (tdse_old). ��������� � �����������
	 * ������� (��. mDiffExtractor) ������������ � work.diff.
	 */
	%mDiffExtractor(mvOutDiff = work.diff,
	                mvTableA = &mvLastLoadTrimmed,
	                mvTableB = &mvNewLoadTable,
	                mvKeyList = &mvKeyList,
	                mvNow=&DWL_LOAD_START_DTTM,
	                mvUpdatedTable = &mvLastLoadTable._new
	               );
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mCreateTransportArchive(work.diff, &mvBA, &DWL_LOAD_FROM, &DWL_LOAD_TILL);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	/* ��������� ������� � ���������� ������������ �������. */
	%DWL_UNX_RENAME(&mvLastLoadTable._new, &mvLastLoadTable);
	%if %DWL_NOT_OK %then %goto EXIT;
 
	%mMarkSuccessfulLoad;
	%if %DWL_NOT_OK %then %goto EXIT;
 
%EXIT:
%mend mCreateDiffTransport;
 /**** END OF SOURCE INCLUDED FROM D:\home\ponomarev\svn\mts-etl-trunk\dwh\region\common\mCreateDiffTransport.sas ****/
 
%macro mLoadAPPA;
    %DWL_INIT;
 
	%mCreateDiffTransport(
		/* ��� ���������� �������. ���������� �������� ����������, ��������� ������
		 * � ������ � ��������� ����� �������� (��. mGetLoadParams).
	     */
		mvBA = APPA,
		/* ����� �����, ������������ ���������� ���� ������ � �������.
		 */
		mvKeyList = app_n effective_from _row_id,
		/* ������ �������� �� Oracle ���������� ������.
		 */
		mvLoadActualData=mGetAPPA);
    %if %DWL_NOT_OK %then %goto EXIT;
%EXIT:
    %DWL_TERM;
%mend mLoadAPPA;
 
/* ���������� �� mCreateDiffTransport.
 */
%macro mGetAPPA(mvNewLoad);
    proc sql noprint;
		connect to oracle as ORA
            ( path = &CRMC_TNS user = &CRMC_USER password = &CRMC_PASS buffsize=5000 preserve_comments );
 
		create table new_appa as
			select
                TERMINAL_DEVICE_ID           as app_n,
				date_from                    as effective_from  length=6   format=datetime.,
                coalesce(date_to,
                    "01JAN2040 00:00:00"dt)  as effective_to    length=6   format=datetime.,
                PERSONAL_ACCOUNT_ID          as acc_id
           	from connection to ORA
				(
					SELECT
						actd.TERMINAL_DEVICE_ID,
						actd.DATE_FROM,    			
						actd.DATE_TO,      			
						actd.PERSONAL_ACCOUNT_ID
					FROM
						cust.personal_account_td actd
					WHERE 1=1
					%if "&DWL_ROWNUM" ^= "" %then %do;
						AND rownum < &DWL_ROWNUM
					%end;	
				  );
    quit;
    %if %DWL_NOT_OK %then %goto EXIT;
 
    proc sort data=new_appa;
        by app_n effective_from;
    run;
    %if %DWL_NOT_OK %then %goto EXIT;
 
	/* ��������� ������� _row_id, ���������� ������ ������ ������ (app_n, effective_from)
	 */	
	data &mvNewLoad / view = &mvNewLoad;
		attrib
			_row_id length=3	label="Unique id of row within a group (acc_app_id, effective_from)"
			;
		set new_appa;
		by app_n effective_from;
 
		if first.effective_from then _row_id = 0;
		else _row_id + 1;
	run;
    %if %DWL_NOT_OK %then %goto EXIT;
%EXIT:
%mend mGetAPPA;
 
/* ������� ����� ��� ������������� ��������. */
%macro DWL_ENTRY_POINT;
	%let DWL_ROWNUM =;
    %mLoadAPPA;
%mend DWL_ENTRY_POINT;
 
/* ������� ����� ��� ��������� �������. (submit � ������� ������� � mvTestRun=1). */
%macro DWL_TEST;
	%let DWL_FIRST_LOAD=0; /* ����� ����������� � ���� ��������� - ������ � 1, ����� � 0. */
 
	%if &DWL_FIRST_LOAD %then %do;
		%let DWL_ROWNUM = 3000;
	%end; %else %do;
		%let DWL_ROWNUM = 5000;
 
		/* ������ load_till ��������� �������� �������� � ���������,
		 * ����� ��������������� �������� (DWL_LOAD_FROM=LAST_SUCCESSFUL_LOAD)
		 * � ��� �� ���� ����� �������� (������ ��� �������� �����).
		 */
		%local mvMaxLoadId;
		proc sql noprint;
			select max(load_id) format 8. into: mvMaxLoadId from MTS_LOGS.LOADS_BA_STATUS
			where successful = 1;
		quit;
		%if %DWL_NOT_OK %then %goto EXIT;
 
		proc sql;
			update MTS_LOGS.LOADS_BA_STATUS
			set load_till = %sysfunc(date(), 8.) - 2
			where load_id = &mvMaxLoadId;
		quit;
		%if %DWL_NOT_OK %then %goto EXIT;
	%end;
    %mLoadAPPA;
%EXIT:
%mend DWL_TEST;
 
 
%DWL_START_LOADING;
%DWL_ENTRY_POINT;
