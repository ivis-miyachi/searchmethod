--
-- PostgreSQL database dump
--

\restrict BjszP1IqqOxHSl2Z5Of76BduDJm54FhM5dVgdDjSPc8kcEs9fJNUw9ynJSy47nG

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: call_method_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.call_method_table (
    id integer NOT NULL,
    caller_id integer,
    callee_id integer
);


ALTER TABLE public.call_method_table OWNER TO postgres;

--
-- Name: call_method_table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.call_method_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.call_method_table_id_seq OWNER TO postgres;

--
-- Name: call_method_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.call_method_table_id_seq OWNED BY public.call_method_table.id;


--
-- Name: class_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.class_table (
    id integer NOT NULL,
    name character varying(128),
    file character varying(128)
);


ALTER TABLE public.class_table OWNER TO postgres;

--
-- Name: class_table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.class_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.class_table_id_seq OWNER TO postgres;

--
-- Name: class_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.class_table_id_seq OWNED BY public.class_table.id;


--
-- Name: endpoint_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.endpoint_table (
    id integer NOT NULL,
    endpoint character varying(128),
    http_method character varying(16),
    method_id integer,
    type character varying(16) DEFAULT 'url'::character varying
);


ALTER TABLE public.endpoint_table OWNER TO postgres;

--
-- Name: endpoint_table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.endpoint_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.endpoint_table_id_seq OWNER TO postgres;

--
-- Name: endpoint_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.endpoint_table_id_seq OWNED BY public.endpoint_table.id;


--
-- Name: inherit_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inherit_table (
    id integer NOT NULL,
    parent_id integer,
    child_id integer
);


ALTER TABLE public.inherit_table OWNER TO postgres;

--
-- Name: inherit_table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inherit_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inherit_table_id_seq OWNER TO postgres;

--
-- Name: inherit_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inherit_table_id_seq OWNED BY public.inherit_table.id;


--
-- Name: method_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.method_table (
    id integer NOT NULL,
    file character varying(128),
    class_id integer,
    method_name character varying(128)
);


ALTER TABLE public.method_table OWNER TO postgres;

--
-- Name: method_table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.method_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.method_table_id_seq OWNER TO postgres;

--
-- Name: method_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.method_table_id_seq OWNED BY public.method_table.id;


--
-- Name: call_method_table id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_method_table ALTER COLUMN id SET DEFAULT nextval('public.call_method_table_id_seq'::regclass);


--
-- Name: class_table id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_table ALTER COLUMN id SET DEFAULT nextval('public.class_table_id_seq'::regclass);


--
-- Name: endpoint_table id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.endpoint_table ALTER COLUMN id SET DEFAULT nextval('public.endpoint_table_id_seq'::regclass);


--
-- Name: inherit_table id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inherit_table ALTER COLUMN id SET DEFAULT nextval('public.inherit_table_id_seq'::regclass);


--
-- Name: method_table id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.method_table ALTER COLUMN id SET DEFAULT nextval('public.method_table_id_seq'::regclass);


--
-- Data for Name: call_method_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.call_method_table (id, caller_id, callee_id) FROM stdin;
1	4	3
2	5	4
3	6	5
4	7	4
5	8	7
6	9	3
8	11	10
9	12	11
10	13	11
11	14	15
12	14	5
13	10	14
14	16	17
15	18	17
16	18	3
17	16	3
18	10	5
19	19	10
20	20	10
21	3	21
22	22	23
23	24	22
24	25	22
25	27	28
26	29	28
27	30	31
28	31	32
29	31	33
30	34	35
31	36	34
32	37	36
33	38	37
34	39	36
35	40	36
36	41	42
37	43	41
38	44	43
39	39	44
40	45	44
41	46	45
42	47	42
43	41	47
44	48	49
45	50	49
46	51	52
47	53	51
48	54	51
49	55	53
50	51	56
51	57	58
52	59	57
53	60	59
54	61	59
55	58	62
56	63	62
57	64	65
58	66	65
59	67	68
60	68	69
61	68	70
62	71	72
63	73	72
64	74	72
65	75	72
66	76	72
67	77	72
68	78	72
69	79	72
70	80	72
71	81	72
72	82	72
73	6	71
74	83	71
75	84	73
76	85	73
77	86	73
78	87	84
79	88	85
80	89	86
81	90	74
82	48	81
83	80	81
84	91	81
85	92	81
86	93	79
87	94	79
88	95	78
89	96	78
90	48	78
91	11	78
92	96	11
\.


--
-- Data for Name: class_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class_table (id, name, file) FROM stdin;
3	FileInstance	invenio_files_rest/models.py
4	ObjectVersion	invenio_files_rest/models.py
5	ObjectResource	invenio_files_rest/views.py
6	WidgetBucket	weko_gridlayout/utils.py
7	ObjectResource	invenio_file_rest/views.py
8	ExportView	weko_authors/admin.py
9	FileInstance	invenio_files_rest/modles.py
10	ItemBulkExport	weko_search_ui/admin.py
11	HarvestSettingView	invenio_oaiharvester/admin.py
12	ItemTypes	weko_records/api.py
13	ItemImportView	weko_search_ui/admin.py
14	ActivityActionResource	weko_workflow/views.py
15	StatisticMail	weko_admin/utils.py
16	FeedbackMailHistory	weko_admin/models.py
17	FeedbackMailFaild	weko_admin/models.py
18	Indexes	weko_index_tree/api.py
19	WekoDeposit	weko_deposit/api.py
20	IndexActionResource	weko_index_tree/rest.py
21	IndexmanagementAPI	weko_index_tree/rest.py
22	WekoIndexer	weko_deposit/api.py
23	RestrictedAccessSettingView	weko_admin/admin.py
24	InvalidWorkflowError	weko_records_ui/errors.py
25	None	weko_admin/models.py
26	StatisticTarget	weko_admin/models.py
27	StatisticUnit	weko_admin/models.py
28	NeedRestrictedAccess	weko_records_ui/rest.py
29	ResourceListHandler	invenio_resourcesyncserver/api.py
30	ChangeListHandler	invenio_resourcesyncserver/api.py
31	WekoFileRanking	weko_items_ui/rest.py
32	GetFileTerms	weko_records_ui/rest.py
33	FileApplication	weko_records_ui/rest.py
34	WekoFilesStats	weko_records_ui/rest.py
35	WekoFilesGet	weko_records_ui/rest.py
\.


--
-- Data for Name: endpoint_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.endpoint_table (id, endpoint, http_method, method_id, type) FROM stdin;
2	/widget/uploaded/<filename>	GET	8	url
3	/api/admin/ogp_image	GET	9	url
4	/record/<pid_value>/file_preview/<filename>	GET	12	url
5	/record/<pid_value>/files/<filename>	GET	13	url
6	/admin/authors/export/download/<filename>	GET	16	url
7	/admin/items/bulk-export/download	GET	18	url
8	/record/<pid_value>/file/onetime/<filename>	GET	19	url
9	/record/<pid_value>/file/secret/<filename>	GET	20	url
10	/widget/uploaded/<filename>/<community_id>	GET	8	url
11	/admin/harvestsettings/run	POST	24	url
12	harvest-check-schedules		25	task
14	/api/authors/edit	POST	27	url
15	/api/authors/gather	POST	29	url
16			30	tool
17	/admin/items/import/import	POST	38	url
18	/sword/service-document	POST	39	url
19	/depositactivity	POST	40	url
20	/admin/items/import/check	GET	46	url
21	/records/<pid_value>/file_details/<filename>	GET	48	url
22	/records/<pid_value>/secret/<filename>	GET	50	url
23	/api/admin/resend_failed_mail	POST	54	url
24	send-feedback-mail-schedules		55	task
25	/api/tree/index/<index_id>	DELETE	60	url
26	/v1/tree/index/<index_id>	DELETE	61	url
27	/admin/restricted_access	GET	64	url
28	/api/admin/get_init_selection/<selection>	GET	67	url
29	/api/items/check_restricted_content	POST	75	url
30	/api/v1/records/<pid_value>/need-restricted-access	GET	80	url
31	/files/<bucket_id>/<key>	DELETE	83	url
1	/files/<bucket_id>/<key>	GET	6	url
32	/items/export	GET,POST	87	url
33	/resync/<index_id>/<record_id>/file_content.zip	GET	88	url
34	/resync/<index_id>/<record_id>/change_dump_content.zip	GET	89	url
35	/api/v1/ranking/<pid_value>/files	GET	90	url
36	/api/v1/records/<pid_value>/files/<file_name>/terms	GET	91	url
37	/api/v1/records/<pid_value>/files/<file_name>/application	POST	92	url
38	/records/<pid_value>	GET	48	url
39	/api/v1/records/<pid_value>/files/<filename>/stats	GET	95	url
40	/api/v1/records/<pid_value>/files/<filename>	GET	80	url
41	/api/v1/records/<pid_value>/files/<filename>	GET	96	url
\.


--
-- Data for Name: inherit_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inherit_table (id, parent_id, child_id) FROM stdin;
\.


--
-- Data for Name: method_table; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.method_table (id, file, class_id, method_name) FROM stdin;
3	invenio_files_rest/models.py	3	send_file
4	invenio_files_rest/models.py	4	send_file
5	invenio_files_rest/views.py	5	send_object
6	invenio_files_rest/views.py	5	get
7	weko_gridlayout/utils.py	6	get_file
8	weko_gridlayout/views.py	\N	uploaded_file
9	weko_admin/views.py	\N	get_ogp_image
10	weko_records_ui/fd.py	\N	_download_file
11	weko_records_ui/fd.py	\N	file_ui
12	weko_records_ui/fd.py	\N	file_preview_ui
13	weko_records_ui/fd.py	\N	file_download_ui
14	weko_records_ui/pdf.py	\N	make_combined_pdf
15	invenio_file_rest/views.py	7	send_object
16	weko_authors/admin.py	8	download
17	invenio_files_rest/modles.py	9	send_file
18	weko_search_ui/admin.py	10	download
19	weko_records_ui/fd.py	\N	file_download_onetime
20	weko_records_ui/fd.py	\N	file_download_secret
21	invenio_previewer/api.py	\N	convert_to
22	invenio_oaiharvester/tasks.py	\N	run_harvesting
23	invenio_oaiharvester/harvester.py	\N	list_records
24	invenio_oaiharvester/admin.py	11	run
25	invenio_oaiharvester/tasks.py	\N	check_schedules_and_run
27	weko_authors/views.py	\N	update_author
28	weko_deposit/tasks.py	\N	update_items_by_authorInfo
29	weko_authors/views.py	\N	gatherById
30	scripts/demo/renew_all_item_types.py	\N	main
31	weko_records/api.py	12	reload
32	weko_records/api.py	12	update_property_enum
33	weko_records/api.py	12	update_attribute_options
34	weko_search_ui/utils.py	\N	register_item_metadata
35	weko_search_ui/utils.py	\N	get_thumbnail_key
36	weko_search_ui/utils.py	\N	import_items_to_system
37	weko_search_ui/tasks.py	\N	import_item
38	weko_search_ui/admin.py	13	import_items
39	weko_swordserver/views.py	\N	post_service_document
40	weko_workflow/views.py	14	post
41	weko_search_ui/utils.py	\N	read_stats_file
42	weko_search_ui/utils.py	\N	handle_get_all_id_in_item_type
43	weko_search_ui/utils.py	\N	unpackage_import_file
44	weko_search_ui/utils.py	\N	check_import_items
45	weko_search_ui/tasks.py	\N	check_import_items_task
46	weko_search_ui/admin.py	13	check
47	weko_search_ui/utils.py	\N	handle_check_metadata_not_existed
48	weko_records_ui/views.py	\N	default_view_method
49	weko_records_ui/views.py	\N	_get_show_secret_url_button
50	weko_records_ui/views.py	\N	create_secret_url_and_send_mail
51	weko_admin/utils.py	15	send_mail_to_one
52	weko_admin/models.py	16	create
53	weko_admin/utils.py	15	send_mail_to_all
54	weko_admin/views.py	\N	resend_failed_mail
55	weko_admin/tasks.py	\N	send_feedback_mail
56	weko_admin/models.py	17	create
57	weko_index_tree/api.py	18	delete_by_action
58	weko_deposit/api.py	19	delete_by_index_tree_id
59	weko_index_tree/utils.py	\N	perform_delete_index
60	weko_index_tree/rest.py	20	delete
61	weko_index_tree/rest.py	21	delete_v1
62	weko_deposit/api.py	22	get_pid_by_es_scroll
63	weko_deposit/api.py	19	update_pid_by_index_tree_id
64	weko_admin/admin.py	23	index
65	weko_admin/utils.py	\N	get_restricted_access
66	weko_records_ui/errors.py	24	get_this_message
67	weko_admin/views.py	\N	get_init_selection
68	weko_admin/utils.py	\N	get_unit_stats_report
69	weko_admin/models.py	26	get_target_by_id
70	weko_admin/models.py	27	get_all_stats_report_unit
71	invenio_files_rest/views.py	5	get_object
72	weko_records_ui/permission.py	\N	check_file_download_permission
73	weko_items_ui/utils.py	\N	_export_item
74	weko_items_ui/utils.py	\N	get_file_download_data
75	weko_items_ui/views.py	\N	check_restricted_content
76	weko_records/utils.py	\N	sort_meta_data_by_options
77	weko_records_ui/fd.py	\N	file_list_ui
78	weko_records_ui/permissions.py	\N	file_permission_factory
79	weko_records_ui/permissions.py	\N	get_permission
80	weko_records_ui/rest.py	28	get_v1
81	weko_records_ui/utils.py	\N	get_file_info_list
82	weko_records_ui/views.py	\N	check_file_permission
83	invenio_files_rest/views.py	5	delete
84	weko_items_ui/utils.py	\N	export_items
85	invenio_resourcesyncserver/api.py	29	get_record_content_file
86	invenio_resourcesyncserver/api.py	30	get_record_content_file
87	weko_items_ui/views.py	\N	export
88	invenio_resourcesyncserver/views.py	\N	file_content
89	invenio_resourcesyncserver/views.py	\N	change_dump_content
90	weko_items_ui/rest.py	31	get_v1
91	weko_records_ui/rest.py	32	get_v1
92	weko_records_ui/rest.py	33	post_v1
93	weko_records_ui/views.py	\N	check_file_permission_period
94	weko_records_ui/views.py	\N	get_file_permission
95	weko_records_ui/rest.py	34	get_v1
96	weko_records_ui/rest.py	35	get_v1
\.


--
-- Name: call_method_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.call_method_table_id_seq', 92, true);


--
-- Name: class_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_table_id_seq', 36, true);


--
-- Name: endpoint_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.endpoint_table_id_seq', 41, true);


--
-- Name: inherit_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inherit_table_id_seq', 1, false);


--
-- Name: method_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.method_table_id_seq', 97, true);


--
-- Name: call_method_table call_method_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_method_table
    ADD CONSTRAINT call_method_table_pkey PRIMARY KEY (id);


--
-- Name: class_table class_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_table
    ADD CONSTRAINT class_table_pkey PRIMARY KEY (id);


--
-- Name: endpoint_table endpoint_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.endpoint_table
    ADD CONSTRAINT endpoint_table_pkey PRIMARY KEY (id);


--
-- Name: inherit_table inherit_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inherit_table
    ADD CONSTRAINT inherit_table_pkey PRIMARY KEY (id);


--
-- Name: method_table method_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.method_table
    ADD CONSTRAINT method_table_pkey PRIMARY KEY (id);


--
-- Name: call_method_table call_method_table_callee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_method_table
    ADD CONSTRAINT call_method_table_callee_id_fkey FOREIGN KEY (callee_id) REFERENCES public.method_table(id);


--
-- Name: call_method_table call_method_table_caller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_method_table
    ADD CONSTRAINT call_method_table_caller_id_fkey FOREIGN KEY (caller_id) REFERENCES public.method_table(id);


--
-- Name: endpoint_table endpoint_table_method_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.endpoint_table
    ADD CONSTRAINT endpoint_table_method_id_fkey FOREIGN KEY (method_id) REFERENCES public.method_table(id);


--
-- Name: inherit_table inherit_table_child_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inherit_table
    ADD CONSTRAINT inherit_table_child_id_fkey FOREIGN KEY (child_id) REFERENCES public.class_table(id);


--
-- Name: inherit_table inherit_table_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inherit_table
    ADD CONSTRAINT inherit_table_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.class_table(id);


--
-- Name: method_table method_table_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.method_table
    ADD CONSTRAINT method_table_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.class_table(id);


--
-- PostgreSQL database dump complete
--

\unrestrict BjszP1IqqOxHSl2Z5Of76BduDJm54FhM5dVgdDjSPc8kcEs9fJNUw9ynJSy47nG

