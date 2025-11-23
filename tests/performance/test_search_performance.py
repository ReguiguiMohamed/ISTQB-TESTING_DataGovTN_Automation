import pytest
import time
import statistics
from pages.home_page import HomePage
from pages.search_page import SearchPage
from config import Config


@pytest.mark.performance
def test_search_response_time_under_threshold(browser):
    """
    Test that search returns results within a time threshold.
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    start_time = time.time()
    search_page.search("education")
    end_time = time.time()

    response_time = end_time - start_time

    # Use a specific performance threshold
    threshold = getattr(Config, 'PERFORMANCE_THRESHOLD', 5.0)  # Default to 5 seconds

    print(f"Search completed in {response_time:.2f} seconds.")

    assert response_time <= threshold, (
        f"Search took {response_time:.2f}s, exceeding limit of {threshold}s"
    )
    assert len(search_page.get_results_titles()) > 0, "Search performance test failed to return results."


@pytest.mark.performance
def test_search_performance_multiple_queries(browser):
    """
    Test search performance across multiple different queries.
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    # Test search performance with various query types
    test_queries = [
        "education",      # Common term
        "health",         # Common term
        "data",           # Very common term
        "transport",      # Common term
        "environnement",  # Common term in French
    ]

    response_times = []
    successful_searches = 0

    for query in test_queries:
        start_time = time.time()
        search_page.search(query)
        end_time = time.time()

        response_time = end_time - start_time
        response_times.append(response_time)

        # Verify results exist
        results = search_page.get_results_titles()
        if len(results) > 0:
            successful_searches += 1

        print(f"Query '{query}' completed in {response_time:.2f}s with {len(results)} results")

    # Calculate performance metrics
    avg_response_time = statistics.mean(response_times)
    median_response_time = statistics.median(response_times)
    max_response_time = max(response_times)
    min_response_time = min(response_times)

    # Set performance thresholds
    avg_threshold = getattr(Config, 'PERFORMANCE_THRESHOLD', 5.0)
    max_threshold = avg_threshold * 2  # Max response time can be higher

    print(f"Performance Metrics:")
    print(f"  Average: {avg_response_time:.2f}s")
    print(f"  Median: {median_response_time:.2f}s")
    print(f"  Max: {max_response_time:.2f}s")
    print(f"  Min: {min_response_time:.2f}s")

    # Verify performance metrics
    assert avg_response_time <= avg_threshold, (
        f"Average search time {avg_response_time:.2f}s exceeds threshold of {avg_threshold}s"
    )
    assert max_response_time <= max_threshold, (
        f"Max search time {max_response_time:.2f}s exceeds threshold of {max_threshold}s"
    )
    assert successful_searches == len(test_queries), (
        f"Only {successful_searches}/{len(test_queries)} searches returned results"
    )


@pytest.mark.performance
def test_search_performance_no_results(browser):
    """
    Test performance when search returns no results (edge case).
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    # Use a query that should return no results
    rare_query = "xyz123qwerty999"  # Highly unlikely to match any dataset

    start_time = time.time()
    search_page.search(rare_query)
    end_time = time.time()

    response_time = end_time - start_time

    # Time threshold for no results search
    threshold = getattr(Config, 'PERFORMANCE_THRESHOLD', 5.0)

    print(f"No-results search completed in {response_time:.2f} seconds.")

    # Verify no results message appears
    assert search_page.has_no_results_message(), "No results message should appear for rare query"

    # Response time should still be within threshold
    assert response_time <= threshold, (
        f"No-results search took {response_time:.2f}s, exceeding limit of {threshold}s"
    )


@pytest.mark.performance
def test_search_performance_different_result_counts(browser):
    """
    Test performance with queries that return different numbers of results.
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    # Define test queries based on expected result count
    test_cases = [
        ("data", "high"),      # Should return many results
        ("a", "high"),         # Very generic term, many results
        ("education", "medium"),  # Moderate number of results
        ("specific", "low"),   # More specific, fewer results
    ]

    performance_results = {}

    for query, expected_type in test_cases:
        start_time = time.time()
        search_page.search(query)
        end_time = time.time()

        response_time = end_time - start_time
        result_count = len(search_page.get_results_titles())

        performance_results[query] = {
            'response_time': response_time,
            'result_count': result_count,
            'expected_type': expected_type
        }

        print(f"Query '{query}': {response_time:.2f}s for {result_count} results")

    # Verify that all searches completed within reasonable time
    for query, data in performance_results.items():
        threshold = getattr(Config, 'PERFORMANCE_THRESHOLD', 5.0)
        assert data['response_time'] <= threshold, (
            f"Search for '{query}' took {data['response_time']:.2f}s, "
            f"exceeding threshold of {threshold}s"
        )


@pytest.mark.performance
def test_consecutive_search_performance(browser):
    """
    Test performance when performing multiple searches in sequence.
    This tests for potential memory leaks or performance degradation.
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    test_queries = [
        "education",
        "health",
        "data",
        "transport",
        "environnement"
    ]

    response_times = []

    # Perform consecutive searches
    for i, query in enumerate(test_queries):
        if i > 0:
            # Navigate back to search page if needed
            search_page.open()

        start_time = time.time()
        search_page.search(query)
        end_time = time.time()

        response_time = end_time - start_time
        response_times.append(response_time)

        print(f"Consecutive search {i+1} ('{query}'): {response_time:.2f}s")

    # Analyze performance consistency
    if len(response_times) > 1:
        time_differences = [abs(response_times[i] - response_times[i-1])
                           for i in range(1, len(response_times))]
        max_difference = max(time_differences)

        # Ensure there isn't dramatic performance degradation between searches
        # Max difference should be reasonable (e.g., not more than 2 seconds difference)
        assert max_difference <= 2.0, (
            f"Large performance difference detected between consecutive searches: {max_difference:.2f}s"
        )

    # Verify all searches completed within threshold
    threshold = getattr(Config, 'PERFORMANCE_THRESHOLD', 5.0)
    for i, response_time in enumerate(response_times):
        assert response_time <= threshold, (
            f"Consecutive search {i+1} took {response_time:.2f}s, "
            f"exceeding threshold of {threshold}s"
        )