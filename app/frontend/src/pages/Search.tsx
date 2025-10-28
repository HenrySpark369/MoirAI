import { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Autocomplete,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useMatching } from '../hooks/useMatching';
import type { Student } from '../types';

const SearchPage = () => {
  const { popularSkills, isLoadingPopular, searchStudents, getSuggestedSkills } =
    useMatching();
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Student[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setIsSearching(true);
    setError(null);
    try {
      const response = await searchStudents({
        skills: selectedSkills,
        query: searchQuery,
      });
      setSearchResults(response.students);
    } catch (err) {
      setError('Failed to perform search');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Find Talented Students
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search Query"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter keywords, project names, or descriptions"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Autocomplete
              multiple
              options={popularSkills || []}
              value={selectedSkills}
              onChange={(_, newValue) => setSelectedSkills(newValue)}
              loading={isLoadingPopular}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Required Skills"
                  placeholder="Select skills"
                />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    label={option}
                    {...getTagProps({ index })}
                    key={option}
                  />
                ))
              }
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={isSearching}
              startIcon={
                isSearching ? <CircularProgress size={20} /> : <SearchIcon />
              }
            >
              {isSearching ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {searchResults.map((student) => (
          <Grid key={student.id} item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {student.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {student.academicProfile.major} - Year{' '}
                  {student.academicProfile.year}
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Technical Skills
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {student.technicalSkills.map((skill) => (
                      <Chip
                        key={skill}
                        label={skill}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>

                {student.softSkills && student.softSkills.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Soft Skills
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {student.softSkills.map((skill) => (
                        <Chip
                          key={skill}
                          label={skill}
                          size="small"
                          variant="outlined"
                          color="secondary"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
              <CardActions>
                <Button size="small" color="primary">
                  View Profile
                </Button>
                <Button size="small" color="primary">
                  Contact
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {searchResults.length === 0 && !isSearching && !error && (
        <Box textAlign="center" py={4}>
          <Typography color="textSecondary">
            No students found. Try adjusting your search criteria.
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default SearchPage;