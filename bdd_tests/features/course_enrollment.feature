Feature: Enroll student to the course

  Scenario: List of courses
    Given user visit / page
    Then it should return a successful response
    And the page shall contains "Courses"
    And the page shall contains "Hello Python"

  Scenario: one Course
    Given user visit /courses/1/ page
    Then it should return a successful response
    And the page shall contains "Hello Python"
    And the page shall contains "long description"

