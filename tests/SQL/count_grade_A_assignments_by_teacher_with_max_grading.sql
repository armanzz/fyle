WITH TeacherGradingCount AS (
    SELECT 
        teacher_id, 
        COUNT(*) AS total_graded_assignments
    FROM 
        assignments
    WHERE 
        state = 'GRADED'
    GROUP BY 
        teacher_id
),
MaxGradingTeacher AS (
    SELECT 
        teacher_id
    FROM 
        TeacherGradingCount
    ORDER BY 
        total_graded_assignments DESC
    LIMIT 1
)
SELECT 
    COUNT(*) AS grade_A_count
FROM 
    assignments
WHERE 
    grade = 'A'
    AND teacher_id = (SELECT teacher_id FROM MaxGradingTeacher);
