export interface User {
  id: string;
  email: string;
  role: 'student' | 'company' | 'admin';
  name: string;
}

export interface Student extends User {
  academicProfile: {
    major: string;
    year: number;
    skills: string[];
  };
  technicalSkills: string[];
  softSkills: string[];
  projects: Project[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface Company extends User {
  companyName: string;
  industry: string;
  vacancies: Vacancy[];
}

export interface Vacancy {
  id: string;
  title: string;
  description: string;
  requiredSkills: string[];
  preferredSkills: string[];
  status: 'open' | 'closed';
}