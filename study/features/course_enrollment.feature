Feature: Enroll student to the course

  Scenario: Find the course
    Given user visit / page
    Then it should return a successful response
    And the page shall contains "Courses"
    And the page shall contains "Hello Python"
