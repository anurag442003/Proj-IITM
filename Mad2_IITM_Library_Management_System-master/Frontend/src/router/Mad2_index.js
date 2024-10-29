import { createRouter, createWebHashHistory } from 'vue-router';
import AboutUs from '../components/AboutUs.vue';
import AdminHome from '../components/AdminHome.vue';
import UsersHome from '../components/Mad2_UsersHome.vue';
import ProfessionalsHome from '../components/Mad2_ProfessionalsHome.vue';
import AddProf from '../components/Mad2_AddProf.vue';
import RenderProf from '../components/Mad2_RenderProf.vue';
import CreateService from '../components/Mad2_CreateService.vue';
import LoginPage from '../components/Mad2_LoginPage.vue';
import RegistrationPage from '../components/Mad2_RegistrationPage.vue';
import SearchResult from '../components/Mad2_SearchResult.vue';
import TransactionLogs from '../components/Mad2_TransactionLogs.vue';
import UpdateProfessional from '../components/Mad2_UpdateProfessional.vue';
import UpdateService from '../components/Mad2_UpdateService.vue';
import UploadProfessional from '../components/Mad2_UploadProfessional.vue';
import HomePage from '../components/Mad2_HomePage.vue';
import UserProfile from '../components/Mad2_UserProfile.vue';
import Approve from '../components/Mad2_Approve.vue';
import Activate from '../components/Mad2_Activate.vue';
import RateProfessional from '../components/Mad2_RateProfessional.vue';
import SummaryGraph from '../components/Mad2_SummaryGraph.vue';
import ActivityPage from '../components/Mad2_ActivityPage.vue';
import RequestList from '@/components/Mad2_RequestList.vue';
import DetailView from '@/components/Mad2_DetailView.vue';
import MoreDetails from '@/components/Mad2_MoreDetails.vue';
import AllDetails from '@/components/Mad2_AllDetails.vue';
import Comments from '@/components/Mad2_Comments.vue';

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/userprofile/:userId', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true } },
  { path: '/rate/:professionalId', name: 'RateProfessional', component: RateProfessional, props: true, meta: { requiresAuth: true } },
  { path: '/users-home', name: 'UsersHome', component: UsersHome, meta: { requiresAuth: true } },
  { path: '/approve', name: 'Approve', component: Approve, meta: { requiresAuth: true } },
  { path: '/activate', name: 'Activate', component: Activate, meta: { requiresAuth: true } },
  { path: '/detail_view/:professionalId/:userId', name: 'DetailView', component: DetailView, meta: { requiresAuth: true } },
  { path: '/all_details/:userId', name: 'AllDetails', component: AllDetails, meta: { requiresAuth: true } },
  { path: '/more_details/:professionalId/:userId', name: 'MoreDetails', component: MoreDetails, meta: { requiresAuth: true } },
  { path: '/professionals-home', name: 'ProfessionalsHome', component: ProfessionalsHome, meta: { requiresAuth: true } },
  { path: '/admin-home', name: 'AdminHome', component: AdminHome, meta: { requiresAuth: true } },
  { path: '/get_all_comments/:professionalId', name: 'Comments', component: Comments, meta: { requiresAuth: true } },
  { path: '/about', name: 'AboutUs', component: AboutUs },
  { path: '/addprof', name: 'AddProf', component: AddProf, meta: { requiresAuth: true } },
  { path: '/renderprof', name: 'RenderProf', component: RenderProf, meta: { requiresAuth: true } },
  { path: '/activity-data/:professionalId', name: 'ActivityPage', component: ActivityPage, meta: { requiresAuth: true } },
  { path: '/request-list', name: 'RequestList', component: RequestList, meta: { requiresAuth: true } },
  { path: '/createcategory', name: 'CreateCategory', component: CreateService, meta: { requiresAuth: true } },
  { path: '/login', name: 'LoginPage', component: LoginPage },
  { path: '/register', name: 'RegistrationPage', component: RegistrationPage },
  { path: '/searchresult/:query', name: 'searchResult', component: SearchResult },
  { path: '/transactionlogs', name: 'TransactionLogs', component: TransactionLogs, meta: { requiresAuth: true } },
  { path: '/update-professional/:professionalId', name: 'UpdateProfessional', component: UpdateProfessional, meta: { requiresAuth: true } },
  { path: '/update-service/:serviceId', name: 'UpdateService', component: UpdateService, meta: { requiresAuth: true } },
  { path: '/upload-professional/:serviceId', name: 'UploadProfessional', component: UploadProfessional, meta: { requiresAuth: true } },
  { path: '/create-service', name: 'CreateService', component: CreateService, meta: { requiresAuth: true } },
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
