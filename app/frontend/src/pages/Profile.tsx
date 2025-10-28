import { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Chip,
  Box,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { useStudentProfile } from '../hooks/useStudentProfile';
import type { Student } from '../types';

const profileSchema = yup.object({
  name: yup.string().required('Name is required'),
  academicProfile: yup.object({
    major: yup.string().required('Major is required'),
    year: yup.number().required('Year is required').min(1, 'Invalid year'),
  }),
}).required();

type ProfileFormData = Pick<Student, 'name' | 'academicProfile'>;

const ProfilePage = () => {
  const { profile, isLoading, error, updateProfile, uploadResume } = useStudentProfile();
  const [newSkill, setNewSkill] = useState('');
  const [uploadError, setUploadError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: yupResolver(profileSchema),
    defaultValues: {
      name: profile?.name,
      academicProfile: profile?.academicProfile,
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfile.mutateAsync(data);
    } catch (err) {
      console.error('Failed to update profile:', err);
    }
  };

  const handleAddSkill = () => {
    if (newSkill && profile?.technicalSkills) {
      updateProfile.mutate({
        technicalSkills: [...profile.technicalSkills, newSkill],
      });
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    if (profile?.technicalSkills) {
      updateProfile.mutate({
        technicalSkills: profile.technicalSkills.filter(
          (skill) => skill !== skillToRemove
        ),
      });
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        await uploadResume.mutateAsync(file);
        setUploadError(null);
      } catch (err) {
        setUploadError('Failed to upload resume');
      }
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" mt={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to load profile
        </Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Student Profile
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <TextField
                {...register('name')}
                fullWidth
                label="Full Name"
                margin="normal"
                error={!!errors.name}
                helperText={errors.name?.message}
              />

              <TextField
                {...register('academicProfile.major')}
                fullWidth
                label="Major"
                margin="normal"
                error={!!errors.academicProfile?.major}
                helperText={errors.academicProfile?.major?.message}
              />

              <TextField
                {...register('academicProfile.year')}
                fullWidth
                label="Year"
                type="number"
                margin="normal"
                error={!!errors.academicProfile?.year}
                helperText={errors.academicProfile?.year?.message}
              />

              <Button
                type="submit"
                variant="contained"
                color="primary"
                sx={{ mt: 2 }}
                disabled={updateProfile.isPending}
              >
                {updateProfile.isPending ? 'Saving...' : 'Save Profile'}
              </Button>
            </form>
          </Paper>

          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Technical Skills
            </Typography>

            <Box display="flex" gap={1} mb={2}>
              <TextField
                fullWidth
                label="Add Skill"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
              />
              <Button
                variant="contained"
                onClick={handleAddSkill}
                disabled={!newSkill}
                startIcon={<AddIcon />}
              >
                Add
              </Button>
            </Box>

            <Box display="flex" gap={1} flexWrap="wrap">
              {profile?.technicalSkills?.map((skill) => (
                <Chip
                  key={skill}
                  label={skill}
                  onDelete={() => handleRemoveSkill(skill)}
                />
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Resume
            </Typography>

            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="resume-upload"
            />
            <label htmlFor="resume-upload">
              <Button
                variant="outlined"
                component="span"
                fullWidth
                disabled={uploadResume.isPending}
              >
                {uploadResume.isPending ? 'Uploading...' : 'Upload Resume'}
              </Button>
            </label>

            {uploadError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {uploadError}
              </Alert>
            )}
          </Paper>

          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Inferred Skills
            </Typography>

            <List dense>
              {profile?.softSkills?.map((skill) => (
                <ListItem key={skill}>
                  <ListItemText primary={skill} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ProfilePage;