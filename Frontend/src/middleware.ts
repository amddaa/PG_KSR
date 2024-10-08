import type {NextRequest} from 'next/server';
import {NextResponse} from 'next/server';

export async function middleware(req: NextRequest) {
    const refresh_token = req.cookies.get('refresh');
    const protectedRoutes = ['/profile'];

    //  || !(await verifyToken())
    if (protectedRoutes.some(route => req.nextUrl.pathname.startsWith(route))) {
        if (!refresh_token) {
            return NextResponse.redirect(new URL('/login', req.url));
        }
    }

    return NextResponse.next();
}
