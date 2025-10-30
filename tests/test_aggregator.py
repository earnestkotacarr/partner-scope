"""
Tests for the company aggregator module.
"""
import pytest
from src.core.aggregator import CompanyAggregator, CompanyRecord


class TestCompanyAggregator:
    """Test cases for CompanyAggregator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.aggregator = CompanyAggregator(similarity_threshold=0.8)

    def test_normalize_domain(self):
        """Test domain normalization."""
        # TODO: Add test cases for domain normalization
        assert self.aggregator.normalize_domain('https://www.example.com') == 'example.com'
        assert self.aggregator.normalize_domain('http://example.com/path') == 'example.com'
        assert self.aggregator.normalize_domain('www.example.com') == 'example.com'
        assert self.aggregator.normalize_domain('') == ''
        assert self.aggregator.normalize_domain(None) == ''

    def test_are_duplicates_same_domain(self):
        """Test duplicate detection with same domain."""
        # TODO: Implement test
        pass

    def test_are_duplicates_similar_names(self):
        """Test duplicate detection with similar names."""
        # TODO: Implement test
        pass

    def test_merge_companies(self):
        """Test merging multiple company records."""
        # TODO: Implement test
        pass

    def test_aggregate(self):
        """Test full aggregation pipeline."""
        # TODO: Implement test with mock data from multiple providers
        pass


class TestCompanyRecord:
    """Test cases for CompanyRecord."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        # TODO: Implement test
        pass
