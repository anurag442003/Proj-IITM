import { createRouter, createWebHashHistory } from 'vue-router';
import AboutUs from '../components/Mad2_AboutUs.vue';
import ReaderHome from '../components/Mad2_ReaderHome.vue';
import LibrarianHome from '../components/Mad2_LibrarianHome.vue';
import AddBook from '../components/Mad2_AddBook.vue';
import BorrowBook from '../components/Mad2_BorrowBook.vue';
import CreateSection from '../components/Mad2_CreateSection.vue';
import LoginPage from '../components/Mad2_LoginPage.vue';
import RegistrationPage from '../components/Mad2_RegistrationPage.vue';
import SearchResult from '../components/Mad2_SearchResult.vue';
import TransactionLogs from '../components/Mad2_TransactionLogs.vue';
import UpdateContent from '../components/Mad2_UpdateContent.vue';
import UpdateSection from '../components/Mad2_UpdateSection.vue';
import UploadContent from '../components/Mad2_UploadContent.vue';
import HomePage from '../components/Mad2_HomePage.vue';
import UserProfile from '../components/Mad2_UserProfile.vue';
import ReaderWishlist from '../components/Mad2_ReaderWishlist.vue';
import RateContent from '../components/Mad2_RateContent.vue';
import SummaryGraph from '../components/Mad2_SummaryGraph.vue';
import ActivityPage from '../components/Mad2_ActivityPage.vue';
import RequestList from '@/components/Mad2_RequestList.vue';
import DetailView from '@/components/Mad2_DetailView.vue';

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/userprofile/:userId', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true } },
  { path: '/rate/:contentId', name: 'RateContent', component: RateContent, props: true, meta: { requiresAuth: true } },
  { path: '/wishlist/:userId', name: 'ReaderWishlist', component: ReaderWishlist, meta: { requiresAuth: true } },
  { path: '/reader-home', name: 'ReaderHome', component: ReaderHome, meta: { requiresAuth: true } },
  { path: '/detail_view/:contentId/:userId', name: 'DetailView', component: DetailView, meta: { requiresAuth: true } },
  { path: '/librarian-home', name: 'LibrarianHome', component: LibrarianHome, meta: { requiresAuth: true } },
  { path: '/about', name: 'AboutUs', component: AboutUs },
  { path: '/addbook', name: 'AddBook', component: AddBook, meta: { requiresAuth: true } },
  { path: '/borrowbook', name: 'BorrowBook', component: BorrowBook, meta: { requiresAuth: true } },
  { path: '/activity-data/:contentId', name: 'ActivityPage', component: ActivityPage, meta: { requiresAuth: true } },
  { path: '/request-list', name: 'RequestList', component: RequestList, meta: { requiresAuth: true } },
  { path: '/createcategory', name: 'CreateCategory', component: CreateSection, meta: { requiresAuth: true } },
  { path: '/login', name: 'LoginPage', component: LoginPage },
  { path: '/register', name: 'RegistrationPage', component: RegistrationPage },
  { path: '/searchresult/:query', name: 'searchResult', component: SearchResult },
  { path: '/transactionlogs', name: 'TransactionLogs', component: TransactionLogs, meta: { requiresAuth: true } },
  { path: '/update-content/:contentId', name: 'UpdateContent', component: UpdateContent, meta: { requiresAuth: true } },
  { path: '/update-section/:sectionId', name: 'UpdateSection', component: UpdateSection, meta: { requiresAuth: true } },
  { path: '/upload-content/:sectionId', name: 'UploadContent', component: UploadContent, meta: { requiresAuth: true } },
  { path: '/create-section', name: 'CreateSection', component: CreateSection, meta: { requiresAuth: true } },
  { path: '/summary-graph', name: 'SummaryGraph', component: SummaryGraph, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    checkAuthentication(to, next);
  } else {
    next();
  }
});

function checkAuthentication(to, next) {
  const token = sessionStorage.getItem('token');
  if (!token) {
    console.log('Token not found in session storage. User is not authenticated.');
    if (to.name !== 'LoginPage') {
      next({ path: '/login', query: { redirect: to ? to.fullPath : '/' } });
    } else {
      next();
    }
    return;
  }

  try {
    fetch('http://127.0.0.1:5000/verify', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.authenticated) {
        console.log('User is authenticated:', data.user.username);
        next();
      } else {
        console.log('User is not authenticated.');
        next({ path: '/login', query: { redirect: to ? to.fullPath : '/' } });
      }
    })
    .catch(error => {
      console.error('Error checking login status:', error);
      next({ path: '/login', query: { redirect: to ? to.fullPath : '/' } });
    });
  } catch (error) {
    console.error('Error checking login status:', error);
    next({ path: '/login', query: { redirect: to ? to.fullPath : '/' } });
  }
}

export default router;
