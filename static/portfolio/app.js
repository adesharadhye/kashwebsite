(function () {
  const e = React.createElement;
  const fallbackData = {
    profile: {
      name: 'Kashish',
      role: 'Civil Engineering Professional',
      summary: 'Civil Engineering professional focused on site execution, structural planning, quantity estimation, quality control, and efficient project delivery across diverse construction projects.',
      contact: {
        location: 'India',
        email: 'Add your email'
      },
      skills: [
        'AutoCAD drawings',
        'Quantity estimation',
        'Site supervision',
        'Construction planning',
        'Surveying basics',
        'Concrete and RCC work',
        'Project documentation',
        'Quality and safety checks'
      ],
      experience: [
        {
          title: 'Civil Engineering Portfolio',
          meta: 'Resume-based presentation',
          points: [
            'Prepared to present resume, civil engineering strengths, and downloadable project documents in one place.',
            'Highlights practical civil engineering work such as drawings, estimation, planning, and execution support.',
            'Includes backend-managed PDF uploads so the latest resume and drawing files can be replaced without editing code.'
          ]
        }
      ],
      projects: [
        {
          name: 'Civil Drawing Package',
          description: 'A downloadable PDF drawing can be uploaded from the backend and shared directly with visitors.'
        },
        {
          name: 'Resume Portfolio',
          description: 'A clean personal presentation page that turns resume information into a professional web profile.'
        }
      ]
    },
    documents: {
      resume: null,
      drawing: null
    }
  };

  function Section(props) {
    const sectionProps = Object.assign({}, props, { className: props.className || 'section' });
    delete sectionProps.children;
    return e('section', sectionProps, props.children);
  }

  function DownloadButton({ document, label }) {
    if (!document) {
      return e('button', { className: 'button ghost', disabled: true }, `${label} unavailable`);
    }

    return e('a', { className: 'button', href: document.url, download: true }, label);
  }

  function App() {
    const [data, setData] = React.useState(null);

    function scrollToSection(event, id) {
      event.preventDefault();
      const section = document.getElementById(id);
      if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    React.useEffect(function () {
      fetch('/api/profile/')
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Profile API failed');
          }
          return response.json();
        })
        .then(setData)
        .catch(function () {
          setData(fallbackData);
        });
    }, []);

    if (!data) {
      return e('main', { className: 'loading' }, 'Loading portfolio...');
    }

    const profile = data.profile;
    const documents = data.documents;

    return e(React.Fragment, null,
      e('header', { className: 'topbar' },
        e('a', { className: 'brand', href: '#' }, profile.name),
        e('nav', null,
          e('a', { href: '#skills', onClick: function (event) { scrollToSection(event, 'skills'); } }, 'Skills'),
          e('a', { href: '#projects', onClick: function (event) { scrollToSection(event, 'projects'); } }, 'Projects'),
          e('a', { href: '#downloads', onClick: function (event) { scrollToSection(event, 'downloads'); } }, 'Downloads')
        )
      ),
      e('main', null,
        e(Section, { className: 'hero' },
          e('div', { className: 'hero-copy' },
            e('p', { className: 'eyebrow' }, 'Personal presentation'),
            e('h1', null, profile.name),
            e('h2', null, profile.role),
            e('p', null, profile.summary),
            e('div', { className: 'actions' },
              e(DownloadButton, { document: documents.resume, label: 'Download Resume' }),
              e(DownloadButton, { document: documents.drawing, label: 'Download Drawing' })
            )
          ),
          e('div', { className: 'hero-panel' },
            e('span', null, 'Civil'),
            e('strong', null, 'Engineering'),
            e('small', null, 'Drawings • Estimation • Site Work')
          )
        ),
        e(Section, { className: 'section split' },
          e('div', null,
            e('p', { className: 'eyebrow' }, 'Profile'),
            e('h2', null, 'Practical Civil Engineering Presentation'),
            e('p', null, 'Civil engineering is the art of shaping the world we live in.')
          ),
          e('div', { className: 'contact-box' },
            Object.keys(profile.contact).map(function (key) {
              return e('p', { key: key }, profile.contact[key]);
            })
          )
        ),
        e(Section, { className: 'section', id: 'skills' },
          e('div', { className: 'section-heading' },
            e('p', { className: 'eyebrow' }, 'Capabilities'),
            e('h2', null, 'Civil Engineering Skills')
          ),
          e('div', { className: 'skill-grid' },
            profile.skills.map(function (skill) {
              return e('div', { className: 'skill-card', key: skill }, skill);
            })
          )
        ),
        e(Section, { className: 'section timeline' },
          e('div', { className: 'section-heading' },
            e('p', { className: 'eyebrow' }, 'Experience'),
            e('h2', null, 'Resume Highlights')
          ),
          profile.experience.map(function (item) {
            return e('article', { className: 'experience-card', key: item.title },
              e('div', null,
                e('h3', null, item.title),
                e('p', { className: 'muted' }, item.meta)
              ),
              e('ul', null, item.points.map(function (point) {
                return e('li', { key: point }, point);
              }))
            );
          })
        ),
        e(Section, { className: 'section', id: 'projects' },
          e('div', { className: 'section-heading' },
            e('p', { className: 'eyebrow' }, 'Work'),
            e('h2', null, 'Featured Documents')
          ),
          e('div', { className: 'project-grid' },
            profile.projects.map(function (project) {
              return e('article', { className: 'project-card', key: project.name },
                e('h3', null, project.name),
                e('p', null, project.description)
              );
            })
          )
        ),
        e(Section, { className: 'downloads', id: 'downloads' },
          e('div', null,
            e('p', { className: 'eyebrow' }, 'Downloads'),
            e('h2', null, 'Resume and PDF drawing')
          ),
          e('div', { className: 'actions' },
            e(DownloadButton, { document: documents.resume, label: 'Download Resume PDF' }),
            e(DownloadButton, { document: documents.drawing, label: 'Download Drawing PDF' })
          )
        )
      ),
      e('footer', null,
        e('span', null, `© ${new Date().getFullYear()} ${profile.name}. Civil engineering portfolio.`),
        e('a', { className: 'admin-link', href: '/backend/upload/' }, 'Backend')
      )
    );
  }

  ReactDOM.createRoot(document.getElementById('root')).render(e(App));
}());
