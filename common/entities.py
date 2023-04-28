entities = [

    {

        'entity_name': 'lesson',
        'table_name': 'stream_module_lesson',
        'pk': 'id',
        'query_to_get_data': '''SELECT t1.*, t2.id as stream_module_id, t3.id as stream_id, t4.id as course_id
             FROM stream_module_lesson t1
             JOIN stream_module t2 ON t2.id=t1.stream_module_id
             JOIN stream t3 ON t3.id=t2.stream_id  
             JOIN course t4 ON t4.id=t3.course_id''',
    },

    {
        'entity_name': 'stream',
        'table_name': 'stream',
        'pk': 'id',
        'query_to_get_data': '''SELECT id, start_at, end_at, created_at, updated_at,
                                       deleted_at, is_open, name, homework_deadline_days
                                       FROM stream''',
    },

    {
        'entity_name': 'course',
        'table_name': 'course',
        'pk': 'id',
        'query_to_get_data': '''SELECT id, title, created_at, updated_at, deleted_at, icon_url,
                                       is_auto_course_enroll,is_demo_enroll
                                       FROM course''',
    },

    {
        'entity_name': 'module',
        'table_name': 'stream_module',
        'pk': 'id',
        'query_to_get_data': '''SELECT id, title, created_at, updated_at, order_in_stream, deleted_at
                                FROM stream_module''',
    },

]
